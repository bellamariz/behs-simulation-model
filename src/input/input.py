from behs.energysupply import *
from behs.energystorage import *
from behs.load import *

_SUPPLY_REGISTRY = {
    "constant": ConstantSupply,
    "harvesting": HarvestingSupply,
}

_STORAGE_REGISTRY = {
    "capacitor": Capacitor,
}

_LOAD_REGISTRY = {
    "resistor": Resistor,
    "mcu": MCU,
}


class Input:
    def __init__(self, config: dict, t_vector: list):
        supply_type = config.get("supply", {}).get("type")
        storage_type = config.get("storage", {}).get("type")
        load_type = config.get("load", {}).get("type")

        if supply_type not in _SUPPLY_REGISTRY:
            raise ValueError(f"Unsupported supply type: {supply_type!r}")
        if storage_type not in _STORAGE_REGISTRY:
            raise ValueError(f"Unsupported storage type: {storage_type!r}")
        if load_type not in _LOAD_REGISTRY:
            raise ValueError(f"Unsupported load type: {load_type!r}")

        self.supply = _SUPPLY_REGISTRY[supply_type](t_vector)
        self.storage = _STORAGE_REGISTRY[storage_type]()
        self.load = _LOAD_REGISTRY[load_type]()
