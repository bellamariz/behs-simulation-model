import json
import src.behs.energysupply as supply
import src.behs.energystorage as storage
import src.behs.load as load

SUPPLY_REGISTRY = {
    "constant": supply.ConstantSupply,
    "harvesting": supply.HarvestingSupply,
}

STORAGE_REGISTRY = {
    "capacitor": storage.Capacitor,
}

LOAD_REGISTRY = {
    "resistor": load.Resistor,
    "mcu": load.MCU,
}


def load_config_file(filepath: str) -> dict:
    with open(filepath, "r") as f:
        return json.load(f)


def generate_t_vector(start, end, interval):
    return [start + i *
            interval for i in range(int((end - start) / interval) + 1)]


class Input:
    def __init__(self, config: dict):
        # Load simulation parameters
        t_step = config.get("simulation").get("step")
        t_duration = config.get("simulation").get("duration")

        if t_step is None or t_duration is None:
            raise ValueError(
                "Simulation 'step' and 'duration' must be specified in the config.")

        # Generate time vector for the simulation
        self.t_vector = generate_t_vector(
            start=0, end=t_duration, interval=t_step)

        # Load BEHS parameters
        supply_cfg = config.get("supply")
        storage_cfg = config.get("storage")
        load_cfg = config.get("load")

        supply_type = supply_cfg.get("type")
        storage_type = storage_cfg.get("type")
        load_type = load_cfg.get("type")

        if supply_type not in SUPPLY_REGISTRY:
            raise ValueError(f"Unsupported supply type: {supply_type!r}")
        if storage_type not in STORAGE_REGISTRY:
            raise ValueError(f"Unsupported storage type: {storage_type!r}")
        if load_type not in LOAD_REGISTRY:
            raise ValueError(f"Unsupported load type: {load_type!r}")

        self.supply = SUPPLY_REGISTRY[supply_type](supply_cfg, self.t_vector)
        self.load = LOAD_REGISTRY[load_type](load_cfg, t_step)
        self.storage = STORAGE_REGISTRY[storage_type](
            storage_cfg, self.load.v_on)
