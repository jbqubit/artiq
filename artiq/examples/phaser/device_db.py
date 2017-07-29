# The RTIO channel numbers here are for Phaser on KC705.

core_addr = "192.168.1.71"
vhdcistart = 0
sawgstart = vhdcistart + 12

device_db = {
    "core": {
        "type": "local",
        "module": "artiq.coredevice.core",
        "class": "Core",
        "arguments": {"host": core_addr, "ref_period": 5e-9/6}
    },
    "core_log": {
        "type": "controller",
        "host": "::1",
        "port": 1068,
        "command": "aqctl_corelog -p {port} --bind {bind} " + core_addr
    },
    "core_cache": {
        "type": "local",
        "module": "artiq.coredevice.cache",
        "class": "CoreCache"
    },

    "lpc_vhdci_port0_ttl0": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 0}
    },
    "lpc_vhdci_port0_ttl1": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 1}
    },
    "lpc_vhdci_port0_ttl2": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 2}
    },
    "lpc_vhdci_port0_ttl3": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 3}
    },
    "lpc_vhdci_port0_ttl4": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 4}
    },
    "lpc_vhdci_port0_ttl5": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 5}
    },
    "lpc_vhdci_port0_ttl6": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 6}
    },
    "lpc_vhdci_port0_ttl7": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 7}
    },
    # support for FMC HPC AD9154 prototype board (4 channel SAWG)
    # using ARTIQ phaser demo
    "lpc_vhdci_i2c": {
        "type": "local",
        "module": "artiq.coredevice.i2c",
        "class": "TCA9548A",
        "arguments": {"address": 0x44}
    },
    "sma_ttl_diff": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 8}
    },
    "lpc_vhdci_latch": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 9}
    },
    "lpc_vhdci_clk": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 10}
    },
    "lpc_vhdci_ser": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 11}
    },

    "sysref": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLInOut",
        "arguments": {"channel": sawgstart + 0}
    },
    "converter_spi": {
        "type": "local",
        "module": "artiq.coredevice.spi",
        "class": "NRTSPIMaster",
    },
    "ad9154_spi": {
        "type": "local",
        "module": "artiq.coredevice.ad9154_spi",
        "class": "AD9154",
        "arguments": {"spi_device": "converter_spi", "chip_select": 1}
    },
    "sawg0": {
        "type": "local",
        "module": "artiq.coredevice.sawg",
        "class": "SAWG",
        "arguments": {"channel_base": sawgstart + 1, "parallelism": 2}
    },
    "sawg1": {
        "type": "local",
        "module": "artiq.coredevice.sawg",
        "class": "SAWG",
        "arguments": {"channel_base": sawgstart + 11, "parallelism": 2}
    },
    "sawg2": {
        "type": "local",
        "module": "artiq.coredevice.sawg",
        "class": "SAWG",
        "arguments": {"channel_base": sawgstart + 21, "parallelism": 2}
    },
    "sawg3": {
        "type": "local",
        "module": "artiq.coredevice.sawg",
        "class": "SAWG",
        "arguments": {"channel_base": sawgstart + 31, "parallelism": 2}
    },
    "ttl_sma": "sma_ttl_diff"
}
