import sys
import asyncio
import logging
import subprocess
import traceback
import time

from artiq.protocols import pyon
from artiq.language.units import strip_unit
from artiq.tools import asyncio_process_wait_timeout, asyncio_wait_or_cancel


logger = logging.getLogger(__name__)


class WorkerTimeout(Exception):
    pass


class WorkerWatchdogTimeout(Exception):
    pass


class WorkerError(Exception):
    pass


class Worker:
    def __init__(self, handlers,
                 send_timeout=0.5, term_timeout=1.0,
                 prepare_timeout=15.0, results_timeout=15.0):
        self.handlers = handlers
        self.send_timeout = send_timeout
        self.term_timeout = term_timeout
        self.prepare_timeout = prepare_timeout
        self.results_timeout = results_timeout

        self.rid = None
        self.process = None
        self.watchdogs = dict()  # wid -> expiration (using time.monotonic)

        self.io_lock = asyncio.Lock()
        self.closed = asyncio.Event()

    def create_watchdog(self, t):
        n_user_watchdogs = len(self.watchdogs)
        if -1 in self.watchdogs:
            n_user_watchdogs -= 1
        avail = set(range(n_user_watchdogs + 1)) \
            - set(self.watchdogs.keys())
        wid = next(iter(avail))
        self.watchdogs[wid] = time.monotonic() + strip_unit(t, "s")
        return wid

    def delete_watchdog(self, wid):
        del self.watchdogs[wid]

    def watchdog_time(self):
        if self.watchdogs:
            return min(self.watchdogs.values()) - time.monotonic()
        else:
            return None

    @asyncio.coroutine
    def _create_process(self):
        yield from self.io_lock.acquire()
        try:
            if self.closed.is_set():
                raise WorkerError("Attempting to create process after close")
            self.process = yield from asyncio.create_subprocess_exec(
                sys.executable, "-m", "artiq.master.worker_impl",
                stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        finally:
            self.io_lock.release()

    @asyncio.coroutine
    def close(self):
        self.closed.set()
        yield from self.io_lock.acquire()
        try:
            if self.process is None:
                # Note the %s - self.rid can be None
                logger.debug("worker was not created (RID %s)", self.rid)
                return
            if self.process.returncode is not None:
                logger.debug("worker already terminated (RID %d)", self.rid)
                if self.process.returncode != 0:
                    logger.warning("worker finished with status code %d"
                                   " (RID %d)", self.process.returncode,
                                   self.rid)
                return
            obj = {"action": "terminate"}
            try:
                yield from self._send(obj, self.send_timeout, cancellable=False)
            except:
                logger.warning("failed to send terminate command to worker"
                               " (RID %d), killing", self.rid, exc_info=True)
                self.process.kill()
                return
            try:
                yield from asyncio_process_wait_timeout(self.process,
                                                        self.term_timeout)
            except asyncio.TimeoutError:
                logger.warning("worker did not exit (RID %d), killing", self.rid)
                self.process.kill()
            else:
                logger.debug("worker exited gracefully (RID %d)", self.rid)
        finally:
            self.io_lock.release()

    @asyncio.coroutine
    def _send(self, obj, timeout, cancellable=True):
        assert self.io_lock.locked()
        line = pyon.encode(obj)
        self.process.stdin.write(line.encode())
        self.process.stdin.write("\n".encode())
        ifs = [self.process.stdin.drain()]
        if cancellable:
            ifs.append(self.closed.wait())
        fs = yield from asyncio_wait_or_cancel(
            ifs, timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED)
        if all(f.cancelled() for f in fs):
            raise WorkerTimeout("Timeout sending data to worker")
        for f in fs:
            if not f.cancelled() and f.done():
                f.result()  # raise any exceptions
        if cancellable and self.closed.is_set():
            raise WorkerError("Data transmission to worker cancelled")

    @asyncio.coroutine
    def _recv(self, timeout):
        assert self.io_lock.locked()
        fs = yield from asyncio_wait_or_cancel(
            [self.process.stdout.readline(), self.closed.wait()],
            timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
        if all(f.cancelled() for f in fs):
            raise WorkerTimeout("Timeout sending data to worker")
        if self.closed.is_set():
            raise WorkerError("Data transmission to worker cancelled")
        line = fs[0].result()
        if not line:
            raise WorkerError("Worker ended while attempting to receive data")
        try:
            obj = pyon.decode(line.decode())
        except:
            raise WorkerError("Worker sent invalid PYON data")
        return obj

    @asyncio.coroutine
    def _handle_worker_requests(self):
        while True:
            try:
                yield from self.io_lock.acquire()
                try:
                    obj = yield from self._recv(self.watchdog_time())
                finally:
                    self.io_lock.release()
            except WorkerTimeout:
                raise WorkerWatchdogTimeout
            action = obj["action"]
            if action == "completed":
                return True
            elif action == "pause":
                return False
            del obj["action"]
            if action == "create_watchdog":
                func = self.create_watchdog
            elif action == "delete_watchdog":
                func = self.delete_watchdog
            else:
                func = self.handlers[action]
            try:
                data = func(**obj)
                reply = {"status": "ok", "data": data}
            except:
                reply = {"status": "failed",
                         "message": traceback.format_exc()}
            yield from self.io_lock.acquire()
            try:
                yield from self._send(reply, self.send_timeout)
            finally:
                self.io_lock.release()

    @asyncio.coroutine
    def _worker_action(self, obj, timeout=None):
        if timeout is not None:
            self.watchdogs[-1] = time.monotonic() + timeout
        try:
            yield from self.io_lock.acquire()
            try:
                yield from self._send(obj, self.send_timeout)
            finally:
                self.io_lock.release()
            try:
                completed = yield from self._handle_worker_requests()
            except WorkerTimeout:
                raise WorkerWatchdogTimeout
        finally:
            if timeout is not None:
                del self.watchdogs[-1]
        return completed

    @asyncio.coroutine
    def prepare(self, rid, pipeline_name, expid, priority):
        self.rid = rid
        yield from self._create_process()
        yield from self._worker_action(
            {"action": "prepare",
             "rid": rid,
             "pipeline_name": pipeline_name,
             "expid": expid,
             "priority": priority},
            self.prepare_timeout)

    @asyncio.coroutine
    def run(self):
        completed = yield from self._worker_action({"action": "run"})
        if not completed:
            self.yield_time = time.monotonic()
        return completed

    @asyncio.coroutine
    def resume(self):
        stop_duration = time.monotonic() - self.yield_time
        for wid, expiry in self.watchdogs:
            self.watchdogs[wid] += stop_duration
        completed = yield from self._worker_action({"status": "ok",
                                                    "data": None})
        if not completed:
            self.yield_time = time.monotonic()
        return completed

    @asyncio.coroutine
    def analyze(self):
        yield from self._worker_action({"action": "analyze"})

    @asyncio.coroutine
    def write_results(self):
        yield from self._worker_action({"action": "write_results"},
                                       self.results_timeout)
