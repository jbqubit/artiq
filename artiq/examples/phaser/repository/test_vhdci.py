from artiq.experiment import *

class TestVHDCI(EnvExperiment):
    """test_vhdci
    """
    def build(self):
        print(self.__doc__)
        self.setattr_device("core")
        self.setattr_device("led")
        self.setattr_device("sma_ttl_n")
        self.setattr_device("sma_ttl_p")
        self.setattr_device("lpc_vhdci_port0_ttl0")


    @kernel
    def run(self):
        self.core.reset()
        delay(1 * ms)

        while True:
            self.sma_ttl_n.pulse(1*us)
            self.sma_ttl_p.pulse(1*us)
            self.lpc_vhdci_port0_ttl0.pulse(1*us)
            self.led.pulse(100*ms)
            delay(100*ms)

            self.led.pulse(100 * ms)


