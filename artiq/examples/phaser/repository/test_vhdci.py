from artiq.experiment import *

class TestVHDCI(EnvExperiment):
    """test_vhdci
    """
    def build(self):
        print(self.__doc__)
        self.setattr_device("core")
        self.setattr_device("led")
        self.setattr_device("sma_ttl_diff")


    @kernel
    def run(self):
        self.core.reset()
        delay(300 * us)
        self.sma_ttl_diff.output()
        delay(1 * ms)

        while True:
            self.sma_ttl_diff.pulse(1*us)
            self.led.pulse(100*ms)
            delay(100*ms)


