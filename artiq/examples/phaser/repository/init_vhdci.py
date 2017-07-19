from artiq.experiment import *

class InitVHDCI(EnvExperiment):
    """init_vhdci
    """
    def build(self):
        print(self.__doc__)
        self.setattr_device("core")
        self.setattr_device("lpc_vhdci_clk")
        self.setattr_device("lpc_vhdci_latch")
        self.setattr_device("lpc_vhdci_ser")


    @kernel
    def init_fmc_lpc_vhdci_adapter(self):
        """
        initialization routine for Creotech FMC DIO 32ch lvds a v1.2
        www.ohwr.org/projects/fmc-dio-32chlvdsa/wiki

        IO direction control is set via latches on SN74LV595APWT
        """
        self.lpc_vhdci_ser.off()
        self.lpc_vhdci_clk.off()
        self.lpc_vhdci_latch.off()

        # set all 32 IO lines for output
        for i in range(32):
            delay(1*us)
            self.lpc_vhdci_clk.pulse(1*us)
            self.lpc_vhdci_latch.pulse(1*us)
        
        # TODO:
        # - per-pin input vs output configuration 
        # - temp sensor
        # - EPROM 

    @kernel
    def run(self):
        self.core.reset()
        delay(10 * ms)

        self.init_fmc_lpc_vhdci_adapter()
        


