import json
import src.behs.energysupply as supply
import src.behs.energystorage as storage
import src.behs.load as load
import src.behs.pmic as pmic
from src.eh import eh
import src.program.program as program

CONFIG_FILE_PATH = "src/input/files/config-complete-pmic.json"

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
# TODO: Update function for latest model changes
def load_config_from_ui(values):
    pass


# The Input class configures all the simulation parameters
class Input:
    def __init__(self, config: dict):
        self._init_simulation_params(config)
        self._init_behs_params(config)
        if self.load.type in _UPLOAD_SOFTWARE_REGISTRY:
            self._init_program_params(config)

    # Initialize simulation parameters
    def _init_simulation_params(self, config: dict):
        step = config.get("simulation").get("step")
        duration = config.get("simulation").get("duration")

        if step is None or duration is None:
            raise ValueError(
                "Simulation 'step' and 'duration' must be specified in the config.")

        self.t_step = step
        self.t_vector = _generate_t_vector(
            start=0, end=duration, interval=step)

    # Initialize BEHS parameters
    def _init_behs_params(self, config: dict):
        # Energy Supply
        supply_cfg = config.get("supply")
        supply_type = supply_cfg.get("type")
        if supply_type not in _SUPPLY_REGISTRY:
            raise ValueError(
                f"Unsupported Energy Supply type: {supply_type!r}")
        self.supply = _SUPPLY_REGISTRY[supply_type](
            supply_cfg, self.t_vector, self.t_step)

        # Energy Storage
        storage_cfg = config.get("storage")
        storage_type = storage_cfg.get("type")
        if storage_type not in _STORAGE_REGISTRY:
            raise ValueError(
                f"Unsupported Energy Storage type: {storage_type!r}")
        self.storage = _STORAGE_REGISTRY[storage_type](storage_cfg)

        # Load
        load_cfg = config.get("load")
        load_type = load_cfg.get("type")
        if load_type not in _LOAD_REGISTRY:
            raise ValueError(f"Unsupported Load type: {load_type!r}")
        self.load = _LOAD_REGISTRY[load_type](load_cfg)

        # PMIC (if applicable)
        pmic_cfg = config.get("pmic")
        if pmic_cfg is not None:
            pmic_type = pmic_cfg.get("type")
            if pmic_type not in _PMIC_REGISTRY:
                raise ValueError(f"Unsupported PMIC type: {pmic_type!r}")
            self.pmic = _PMIC_REGISTRY[pmic_type](pmic_cfg)

    def _init_program_params(self, config: dict):
        program_cfg = config.get("program")
        if program_cfg is None:
            raise ValueError(
                "Software program configuration must be specified in the config file")

        program_file = program_cfg.get("filepath")
        if program_file is None:
            raise ValueError(
                "Software program file must be specified in the config file")

        program_clock = program_cfg.get("processing_clock")
        if program_clock is None:
            program_clock = program.DEFAULT_PROCESSING_CLOCK
            print(
                "Warning: Program clock not specified, will use 1ms as default.")
        elif program_clock > self.t_step or program_clock < program.DEFAULT_PROCESSING_CLOCK:
            raise ValueError(
                f"Provided program clock is invalid: {program_clock}.")

        # Get Load's CPU parameters for Program initialization
        load_cfg = config.get("load")
        cpu_active_cost = load_cfg.get("modes").get("active").get("cost")
        cpu_standby_cost = load_cfg.get("modes").get("standby").get("cost")

        # Parse Program object from file and upload to the Load
        prog = program.Program(
            program_file, cpu_active_cost, cpu_standby_cost, program_clock)
        prog.print()
        self.load.upload_software(prog)
