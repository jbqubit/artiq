#[path = "../runtime/kernel_proto.rs"]
mod kernel_proto;

use board::csr;
use core::ptr::{read_volatile, write_volatile};
use ::ArtiqList;
use ::send;
use kernel_proto::*;

const RTIO_O_STATUS_FULL:           u32 = 1;
const RTIO_O_STATUS_UNDERFLOW:      u32 = 2;
const RTIO_O_STATUS_SEQUENCE_ERROR: u32 = 4;
const RTIO_O_STATUS_COLLISION:      u32 = 8;
const RTIO_O_STATUS_BUSY:           u32 = 16;
const RTIO_I_STATUS_EMPTY:          u32 = 1;
const RTIO_I_STATUS_OVERFLOW:       u32 = 2;

pub extern fn init() {
    send(&RTIOInitRequest);
}

pub extern fn get_counter() -> i64 {
    unsafe {
        csr::rtio::counter_update_write(1);
        csr::rtio::counter_read() as i64
    }
}

#[inline(always)]
pub unsafe fn rtio_o_data_write(offset: usize, data: u32) {
    write_volatile(
        csr::rtio::O_DATA_ADDR.offset((csr::rtio::O_DATA_SIZE - 1 - offset) as isize),
        data);
}

#[inline(always)]
pub unsafe fn rtio_i_data_read(offset: usize) -> u32 {
    read_volatile(
        csr::rtio::I_DATA_ADDR.offset((csr::rtio::I_DATA_SIZE - 1 - offset) as isize))
}

#[inline(never)]
unsafe fn process_exceptional_status(timestamp: i64, channel: i32, status: u32) {
    if status & RTIO_O_STATUS_FULL != 0 {
        while csr::rtio::o_status_read() & RTIO_O_STATUS_FULL != 0 {}
    }
    if status & RTIO_O_STATUS_UNDERFLOW != 0 {
        csr::rtio::o_underflow_reset_write(1);
        artiq_raise!("RTIOUnderflow",
            "RTIO underflow at {0} mu, channel {1}, slack {2} mu",
            timestamp, channel as i64, timestamp - get_counter())
    }
    if status & RTIO_O_STATUS_SEQUENCE_ERROR != 0 {
        csr::rtio::o_sequence_error_reset_write(1);
        artiq_raise!("RTIOSequenceError",
            "RTIO sequence error at {0} mu, channel {1}",
            timestamp, channel as i64, 0)
    }
    if status & RTIO_O_STATUS_COLLISION != 0 {
        csr::rtio::o_collision_reset_write(1);
        artiq_raise!("RTIOCollision",
            "RTIO collision at {0} mu, channel {1}",
            timestamp, channel as i64, 0)
    }
    if status & RTIO_O_STATUS_BUSY != 0 {
        csr::rtio::o_busy_reset_write(1);
        artiq_raise!("RTIOBusy",
            "RTIO busy on channel {0}",
            channel as i64, 0, 0)
    }
}

pub extern fn output(timestamp: i64, channel: i32, addr: i32, data: i32) {
    unsafe {
        csr::rtio::chan_sel_write(channel as u32);
        csr::rtio::o_timestamp_write(timestamp as u64);
        csr::rtio::o_address_write(addr as u32);
        rtio_o_data_write(0, data as u32);
        csr::rtio::o_we_write(1);
        let status = csr::rtio::o_status_read();
        if status != 0 {
            process_exceptional_status(timestamp, channel, status);
        }
    }
}

pub extern fn output_wide(timestamp: i64, channel: i32, addr: i32, list: ArtiqList<i32>) {
    unsafe {
        csr::rtio::chan_sel_write(channel as u32);
        csr::rtio::o_timestamp_write(timestamp as u64);
        csr::rtio::o_address_write(addr as u32);
        let data = list.as_slice();
        for i in 0..data.len() {
            rtio_o_data_write(i, data[i] as u32)
        }
        csr::rtio::o_we_write(1);
        let status = csr::rtio::o_status_read();
        if status != 0 {
            process_exceptional_status(timestamp, channel, status);
        }
    }
}

pub extern fn input_timestamp(timeout: i64, channel: i32) -> u64 {
    unsafe {
        csr::rtio::chan_sel_write(channel as u32);
        let mut status;
        loop {
            status = csr::rtio::i_status_read();
            if status == 0 { break }

            if status & RTIO_I_STATUS_OVERFLOW != 0 {
                csr::rtio::i_overflow_reset_write(1);
                break
            }
            if get_counter() >= timeout {
                // check empty flag again to prevent race condition.
                // now we are sure that the time limit has been exceeded.
                let status = csr::rtio::i_status_read();
                if status & RTIO_I_STATUS_EMPTY != 0 { break }
            }
            // input FIFO is empty - keep waiting
        }

        if status & RTIO_I_STATUS_OVERFLOW != 0 {
            artiq_raise!("RTIOOverflow",
                "RTIO input overflow on channel {0}",
                channel as i64, 0, 0);
        }
        if status & RTIO_I_STATUS_EMPTY != 0 {
            return !0
        }

        let timestamp = csr::rtio::i_timestamp_read();
        csr::rtio::i_re_write(1);
        timestamp
    }
}

pub extern fn input_data(channel: i32) -> i32 {
    unsafe {
        csr::rtio::chan_sel_write(channel as u32);
        loop {
            let status = csr::rtio::i_status_read();
            if status == 0 { break }

            if status & RTIO_I_STATUS_OVERFLOW != 0 {
                csr::rtio::i_overflow_reset_write(1);
                artiq_raise!("RTIOOverflow",
                    "RTIO input overflow on channel {0}",
                    channel as i64, 0, 0);
            }
        }

        let data = rtio_i_data_read(0);
        csr::rtio::i_re_write(1);
        data as i32
    }
}

#[cfg(has_rtio_log)]
pub fn log(timestamp: i64, data: &[u8]) {
    unsafe {
        csr::rtio::chan_sel_write(csr::CONFIG_RTIO_LOG_CHANNEL);
        csr::rtio::o_timestamp_write(timestamp as u64);

        let mut word: u32 = 0;
        for i in 0..data.len() {
            word <<= 8;
            word |= data[i] as u32;
            if i % 4 == 0 {
                rtio_o_data_write(0, word);
                csr::rtio::o_we_write(1);
                word = 0;
            }
        }

        word <<= 8;
        rtio_o_data_write(0, word);
        csr::rtio::o_we_write(1);
    }
}

#[cfg(not(has_rtio_log))]
pub fn log(_timestamp: i64, _data: &[u8]) {}

pub mod drtio_dbg {
    use ::send;
    use ::recv;
    use kernel_proto::*;


    #[repr(C)]
    pub struct ChannelState(i32, i64);

    pub extern fn get_channel_state(channel: i32) -> ChannelState {
        send(&DRTIOChannelStateRequest { channel: channel as u32 });
        recv!(&DRTIOChannelStateReply { fifo_space, last_timestamp }
              => ChannelState(fifo_space as i32, last_timestamp as i64))
    }

    pub extern fn reset_channel_state(channel: i32) {
        send(&DRTIOResetChannelStateRequest { channel: channel as u32 })
    }

    pub extern fn get_fifo_space(channel: i32) {
        send(&DRTIOGetFIFOSpaceRequest { channel: channel as u32 })
    }

    #[repr(C)]
    pub struct PacketCounts(i32, i32);

    pub extern fn get_packet_counts() -> PacketCounts {
        send(&DRTIOPacketCountRequest);
        recv!(&DRTIOPacketCountReply { tx_cnt, rx_cnt }
              => PacketCounts(tx_cnt as i32, rx_cnt as i32))
    }

    pub extern fn get_fifo_space_req_count() -> i32 {
        send(&DRTIOFIFOSpaceReqCountRequest);
        recv!(&DRTIOFIFOSpaceReqCountReply { cnt }
              => cnt as i32)
    }
}
