import json
import src.behs.energysupply as supply
import src.behs.energystorage as storage
import src.behs.load as load
import src.behs.pmic as pmic
from src.eh import eh
import src.program.program as program

CONFIG_FILE_PATH = "src/input/files/config.json"

_SUPPLY_REGISTRY = {
    "constant": supply.ConstantSupply,
    "harvesting": supply.HarvestingSupply,
}

_STORAGE_REGISTRY = {
    "capacitor": storage.Capacitor,
}

_LOAD_REGISTRY = {
    "resistor": load.Resistor,
    "mcu": load.MCU,
}

_PMIC_REGISTRY = {
    "boost_buck": pmic.BoostBuckPMIC,
}

_UPLOAD_SOFTWARE_REGISTRY = ["mcu"]

_SET_UP_EH_SUPPLY_PROFILE_REGISTRY = ["harvesting"]


# Generate time vector for simulation
def _generate_t_vector(start, end, interval):
    return [start + i *
            interval for i in range(int((end - start) / interval) + 1)]


# Set up energy profile file for HarvestingSupply class, parsing a real EH dataset from HDF5 to CSV
# It reads the EH dataset and generates a CSV with results, writing to output_filepath.
def set_up_eh_supply_profile_file(supply_cfg):
    if supply_cfg.get("type") in _SET_UP_EH_SUPPLY_PROFILE_REGISTRY:
        output_filepath = supply_cfg.get("profile_filepath")
        eh.teg_dataset_to_csv(output_filepath)


# Load simulation configuration from JSON input file
# For more information, read the docs: /src/input/files/README.md
def load_config_from_file(filepath: str) -> dict:
    with open(filepath, "r") as f:
        return json.load(f)


# Load simulation configuration from UI input values
# TODO: Update func considering the new config.json
def load_config_from_ui(values):
    # Parses input for Energy Storage
    storage_type = values["storage_type"]
    storage_cfg = {"type": storage_type}
    if storage_type == "capacitor":
        storage_cfg["capacitance"] = float(values["storage_capacitance"])
        storage_cfg["v_oper_max"] = float(values["storage_v_oper_max"])

    # Parses input for Energy Supply
    supply_type = values["supply_type"]
    supply_cfg = {"type": supply_type}
    if supply_type == "constant":
        supply_cfg["p_base"] = float(values["supply_p_base"])
    elif supply_type == "harvesting":
        supply_cfg["filename"] = values["supply_filename"]
        supply_cfg["sampling_period"] = float(values["supply_sampling_period"])

    # Parses input for Load
    load_type = values["load_type"]
    load_cfg = {"type": load_type}
    actions_cfg = []
    if load_type == "resistor":
        load_cfg["resistance"] = float(values["load_resistance"])
        load_cfg["p_rating"] = float(values["load_p_rating"])
        load_cfg["v_max"] = float(values["load_v_max"])
    elif load_type == "mcu":
        load_cfg["v_min"] = float(values["load_v_min"])
        load_cfg["v_wake_up"] = float(values["load_v_wake_up"])
        load_cfg["v_oper_low"] = float(values["load_v_oper_low"])
        load_cfg["v_oper_active"] = float(values["load_v_oper_active"])
        load_cfg["v_max"] = float(values["load_v_max"])
        load_cfg["modes"] = {
            "shutdown": float(values["load_mode_shutdown"]),
            "low_power": float(values["load_mode_low_power"]),
            "active": float(values["load_mode_active"]),
        }
        load_cfg["program"] = values["load_program"]

        # Parses input for Actions (if Load is MCU)
        actions_cfg = [
            {"action": "sleeping", "instruction": values["action_sleep_instr"], "cost": float(
                values["action_sleep_cost"])},
            {"action": "sensing", "instruction": values["action_sense_instr"], "cost": float(
                values["action_sense_cost"])},
            {"action": "transmitting", "instruction": values["action_tx_instr"], "cost": float(
                values["action_tx_cost"])},
            {"action": "receiving", "instruction": values["action_rx_instr"], "cost": float(
                values["action_rx_cost"])},
            {"action": "processing", "instruction": values["action_proc_instr"], "cost": float(
                values["action_proc_cost"])},
        ]

    config = {
        "simulation": {
            "duration": float(values["sim_duration"]),
            "step": float(values["sim_step"]),
        },
        "supply": supply_cfg,
        "storage": storage_cfg,
        "load": load_cfg,
        "actions": actions_cfg
    }

    return config


# The Input class configures all the simulation parameters
class Input:
    def __init__(self, config: dict):
        # Load simulation parameters
        t_step = config.get("simulation").get("step")
        t_duration = config.get("simulation").get("duration")

        if t_step is None or t_duration is None:
            raise ValueError(
                "Simulation 'step' and 'duration' must be specified in the config.")

        self.t_step = t_step
        self.t_vector = _generate_t_vector(
            start=0, end=t_duration, interval=t_step)

        # Load BEHS parameters: Energy Supply, Energy Storage, Load
        supply_cfg = config.get("supply")
        storage_cfg = config.get("storage")
        load_cfg = config.get("load")

        supply_type = supply_cfg.get("type")
        storage_type = storage_cfg.get("type")
        load_type = load_cfg.get("type")

        if supply_type not in _SUPPLY_REGISTRY:
            raise ValueError(f"Unsupported supply type: {supply_type!r}")
        if storage_type not in _STORAGE_REGISTRY:
            raise ValueError(f"Unsupported storage type: {storage_type!r}")
        if load_type not in _LOAD_REGISTRY:
            raise ValueError(f"Unsupported load type: {load_type!r}")

        self.supply = _SUPPLY_REGISTRY[supply_type](
            supply_cfg, self.t_vector, self.t_step)
        self.storage = _STORAGE_REGISTRY[storage_type](storage_cfg)
        self.load = _LOAD_REGISTRY[load_type](load_cfg)
        self.pmic = None

        # Load BEHS parameters: PMIC (if applicable)
        pmic_cfg = config.get("pmic")

        if pmic_cfg is not None:
            pmic_type = pmic_cfg.get("type")
            if pmic_type not in _PMIC_REGISTRY:
                raise ValueError(f"Unsupported PMIC type: {pmic_type!r}")
            self.pmic = _PMIC_REGISTRY[pmic_type](pmic_cfg)

        # Upload software to the Load (if applicable)
        if load_type in _UPLOAD_SOFTWARE_REGISTRY:
            program_file = config.get("program_filepath")
            cpu_active_cost = load_cfg.get("modes").get("active").get("cost")
            cpu_standby_cost = load_cfg.get("modes").get("standby").get("cost")

            # Parse Program object from file
            prog = program.Program(
                t_step, program_file, cpu_active_cost, cpu_standby_cost)
            prog.print()

            # Upload Program to the Load
            self.load.upload_software(prog)
