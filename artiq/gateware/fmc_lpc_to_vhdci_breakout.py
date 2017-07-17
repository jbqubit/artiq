from migen.build.generic_platform import *


fmc_lpc_to_vhdci_breakout_io = [
    ("sma_ttl_diff", 0,
     Subsignal("p", Pins("Y23")),
     Subsignal("n", Pins("Y24")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     ),
    ("lpc_vhdci_ext0", 0,
     Subsignal("p", Pins("LPC:LA00_CC_P")),
     Subsignal("n", Pins("LPC:LA00_CC_N")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     ),
    ("lpc_vhdci_ext0", 1,
     Subsignal("p", Pins("LPC:LA01_CC_P")),
     Subsignal("n", Pins("LPC:LA01_CC_N")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     ),
    ("lpc_vhdci_ext0", 2,
     Subsignal("p", Pins("LPC:LA02_P")),
     Subsignal("n", Pins("LPC:LA02_N")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     ),
    ("lpc_vhdci_ext0", 3,
     Subsignal("p", Pins("LPC:LA03_P")),
     Subsignal("n", Pins("LPC:LA03_N")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     ),
    ("lpc_vhdci_ext0", 4,
     Subsignal("p", Pins("LPC:LA04_P")),
     Subsignal("n", Pins("LPC:LA04_N")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     ),
    ("lpc_vhdci_ext0", 5,
     Subsignal("p", Pins("LPC:LA05_P")),
     Subsignal("n", Pins("LPC:LA05_N")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     ),
    ("lpc_vhdci_ext0", 6,
     Subsignal("p", Pins("LPC:LA06_P")),
     Subsignal("n", Pins("LPC:LA06_N")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     ),
    ("lpc_vhdci_ext0", 7,
     Subsignal("p", Pins("LPC:LA07_P")),
     Subsignal("n", Pins("LPC:LA07_N")),
     IOStandard("LVDS_25"), Misc("DIFF_TERM=TRUE")
     )
]