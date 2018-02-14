from artiq.experiment import *


class UrukulTest(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")
        self.setattr_device("urukul0_ch1")
        self.setattr_device("urukul0_ch2")
        self.setattr_device("urukul0_ch3")
        self.setattr_device("led0")

    def p(self, f, *a):
        print(f % a)

    @kernel
    def run(self):
        self.core.reset()
        self.led0.on()
        delay(5*ms)
        self.led0.off()

        self.urukul0_cpld.init(clk_sel=0)
        self.urukul0_ch0.init()
        self.urukul0_ch1.init()
        self.urukul0_ch2.init()
        self.urukul0_ch3.init()

        delay(1000*us)
        self.urukul0_ch0.set(100*MHz)
        self.urukul0_ch0.sw.on()
        self.urukul0_ch0.set_att(10.)

        delay(1000*us)
        self.urukul0_ch1.set(10*MHz, 0.5)
        self.urukul0_ch1.sw.on()
        self.urukul0_ch1.set_att(0.)

        delay(1000*us)
        self.urukul0_ch2.set(400*MHz)
        self.urukul0_ch2.sw.on()
        self.urukul0_ch2.set_att(0.)

        delay(1000*us)
        self.urukul0_ch3.set(1*MHz)
        self.urukul0_ch3.sw.on()
        self.urukul0_ch3.set_att(20.)

        i = 0
        j = 0

        while True:
            self.urukul0_ch0.sw.pulse(5*ms)
            delay(5*ms)

        while False:
            self.led0.pulse(.5*s)
            delay(.5*s)

    @kernel
    def test_att_noise(self, n=1024):
        bus = self.urukul0_cpld.bus
        bus.set_config_mu(_SPI_CONFIG, _SPIT_ATT_WR, _SPIT_ATT_RD)
        bus.set_xfer(CS_ATT, 32, 0)
        for i in range(n):
            delay(5*us)
            bus.write(self.att_reg)
        bus.set_config_mu(_SPI_CONFIG, _SPIT_DDS_WR, _SPIT_DDS_RD)