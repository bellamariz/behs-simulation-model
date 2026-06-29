import random
import pandas as pd

# According to the literature, an BEHS model has one of these three energy profiles:
#
# 1- Energy Neutral:
#     The harvested energy is equal to or exceeds the energy consumed by the system over time.
#     Energy storage is normally used to buffer differences in supply and demand during smaller periods
# 2- Power Neutral:
#     Assumes a zero-storage approach and works under the premise that the energy generated equals the energy consumed.
#     Controls its performance by adapting computer processes to match the energy levels.
# 3- Intermittent Energy:
#     Systems where the power requirements exceed the maximum amount of energy the harvester or storage are capable of supplying.
#     Periods of active operation are mixed with periods for recharging the energy storage.
#
# For now, this model will assume a more simplified behavior, with two types of energy supply:
#
# 1- Constant Supply: A constant power supply (e.g., a battery or regulated source).
# 2- Harvesting Supply: A variable power supply loaded from a real energy harvesting dataset.

from abc import ABC, abstractmethod


# Class EnergySupply for the BEHS simulation model
# It represents the energy supply, a component that provides energy to the system.
class EnergySupply(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        # filepath for the energy supply profile (if applicable)
        self.filepath: str
        self.power_supply: float    # power supply (W) at time t
        self.energy_supply: float  # energy supply (J) at time t
        self.profile: list[float]   # power profile over time (W)

    # Refreshes the energy supply's state at each time step
    @abstractmethod
    def refresh(self, t_index: int, t_step: float) -> None:
        self.power_supply = self.profile[t_index]
        self.energy_supply = self.power_supply * t_step

    # Prints the energy supply's state at given time index
    @abstractmethod
    def print(self, t_index: int, file) -> None:
        print(
            f"Energy Supply: {self.type} --> "
            f"t={t_index},"
            f"power_supply={self.power_supply:.5f}W,"
            f"energy_supply={self.energy_supply:.5f}J",
            file=file
        )


# Class ConstantSupply for the BEHS simulation model, inheriting from EnergySupply Class
# It represents a constant power supply.
class ConstantSupply(EnergySupply):
    def __init__(self, config, t_vector, t_step):
        p_base = config.get("p_base")

        self.type = config.get("type")
        self.filepath = ""
        self.power_supply = 0.0
        self.energy_supply = 0.0
        self.profile = [p_base] * len(t_vector)

    def refresh(self, t_index, t_step):
        super().refresh(t_index, t_step)

    def print(self, t_index, file):
        super().print(t_index, file)


# Class HarvestingSupply for the BEHS simulation model, inheriting from EnergySupply Class
# It represents a variable power supply loaded from a real energy harvesting dataset.
class HarvestingSupply(EnergySupply):
    def __init__(self, config, t_vector, t_step):
        self.SIM_STEP = t_step
        self.SIM_TOTAL_STEPS = len(t_vector)
        self.SAMPLING_PERIOD = config.get("sampling_period")

        self.type = config.get("type")
        self.filepath = config.get("profile_filepath")
        self.power_supply = 0.0
        self.energy_supply = 0.0
        self.profile = self._parse_profile_from_dataset()

    def _parse_profile_from_dataset(self):
        # Reads the CSV file into a dataframe
        df = pd.read_csv(self.filepath, index_col="timestamp")

        # Gets column with power output data
        raw = df["power_out_w"].tolist()
        if not raw:
            print(
                f"Warning: Dataset for {self.filepath} is empty or missing 'power_out_w' column.")
            return [0.0] * self.SIM_TOTAL_STEPS

        # Resamples the power output data to match the simulation time steps
        result = []
        for sim_idx in range(self.SIM_TOTAL_STEPS):
            # Map simulation time step to the dataset's sampling period
            dataset_idx = ((sim_idx * self.SIM_STEP) /
                           self.SAMPLING_PERIOD) % len(raw)

            # Use linear interpolation
            # To better estimate fractional the value between two samples
            lo = int(dataset_idx)
            hi = (lo + 1) % len(raw)
            frac = dataset_idx - lo

            # Append the interpolated value to the result list
            result.append(raw[lo] + frac * (raw[hi] - raw[lo]))

        return result

    def refresh(self, t_index, t_step):
        super().refresh(t_index, t_step)

    def print(self, t_index, file):
        super().print(t_index, file)
