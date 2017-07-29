from artiq.experiment import *


class SAWGTest(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        #self.setattr_device("led")
        self.setattr_device("sma_ttl_diff")

        self.setattr_device("lpc_vhdci_port0_ttl0")
        self.setattr_device("lpc_vhdci_port0_ttl1")
        self.setattr_device("lpc_vhdci_port0_ttl2")
        self.setattr_device("lpc_vhdci_port0_ttl3")

    @kernel
    def run(self):
        self.core.reset()
        delay(10 * ms)
        self.sma_ttl_diff.output()
        #self.led.output()
        self.lpc_vhdci_port0_ttl0.output()
        self.lpc_vhdci_port0_ttl1.output()
        self.lpc_vhdci_port0_ttl2.output()
        self.lpc_vhdci_port0_ttl3.output()

        delay(10*ms)

        while True:
            self.sma_ttl_diff.pulse(500*ns)
            self.lpc_vhdci_port0_ttl0.pulse(1*us)
            self.lpc_vhdci_port0_ttl1.pulse(2 * us)
            self.lpc_vhdci_port0_ttl2.pulse(3 * us)
            self.lpc_vhdci_port0_ttl3.pulse(3 * us)
            #self.led.pulse(100*ms)
            delay(100*ms)
