from artiq.experiment import *

class TestVHDCI(EnvExperiment):
    """test 3U BNC output
    KC705-> FMC-VHDCI adapter -> VHDCI cable -> VHDCI carrier -> IDC cable-> 3U BNC
    """
    def build(self):
        print(self.__doc__)
        self.setattr_device("core")
        self.setattr_device("sma_ttl_diff")
        self.setattr_device("lpc_vhdci_port0_ttl0")
        self.setattr_device("lpc_vhdci_port0_ttl1")
        self.setattr_device("lpc_vhdci_port0_ttl2")
        self.setattr_device("lpc_vhdci_port0_ttl3")
        self.setattr_device("lpc_vhdci_port0_ttl4")
        self.setattr_device("scheduler")


    @kernel
    def run(self):
        self.core.reset()
        delay(1 * ms)
        while True:
            self.sma_ttl_diff.pulse(1*us)
            self.lpc_vhdci_port0_ttl0.pulse(1*us)
            self.lpc_vhdci_port0_ttl1.pulse(1*us)
            self.lpc_vhdci_port0_ttl2.pulse(1*us)
            self.lpc_vhdci_port0_ttl3.pulse(1*us)
            self.lpc_vhdci_port0_ttl4.pulse(1*us)
            delay(100*ms)


