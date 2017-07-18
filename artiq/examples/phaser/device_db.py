# The RTIO channel numbers here are for Phaser on KC705.

core_addr = "192.168.1.71"
vhdcistart = 0

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
    "led": {
        "type": "local",
        "module": "artiq.coredevice.ttl",
        "class": "TTLOut",
        "arguments": {"channel": vhdcistart + 9}
    }
}
