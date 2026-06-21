import random

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
# 1- Constant Supply: A constant voltage supply, e.g., a battery.
# 2- Harvesting Supply: A variable voltage supply, e.g., a solar panel.

from abc import ABC, abstractmethod


# Class EnergySupply for the BEHS simulation model
# It represents the energy supply, a circuit component that provides energy to the system
class EnergySupply(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.voltage: float  # supplied voltage at a given time index, in Voltz
        self.profile: list[float]

    # Shows the voltage being supplied at a given time index
    @abstractmethod
    def refresh(self, t_index: int) -> None:
        self.voltage = self.profile[t_index]

    # Prints the energy supply's state at a given time index
    @abstractmethod
    def print(self, t_index: int, file) -> None:
        print(
            f"Energy Supply: {self.type} --> "
            f"t={t_index},"
            f"voltage={self.voltage:.5f}V",
            file=file
        )


# Class ConstantSupply for the BEHS simulation model, inheriting from EnergySupply Class
# It represents a constant voltage supply
class ConstantSupply(EnergySupply):
    def __init__(self, config, t_vector):
        v_base = config.get("v_base")

        self.type = config.get("type")
        self.voltage = 0.0
        self.profile = [v_base] * len(t_vector)

    def refresh(self, t_index):
        super().refresh(t_index)

    def print(self, t_index, file):
        super().print(t_index, file)


# Class HarvestingSupply for the BEHS simulation model, inheriting from EnergySupply Class
# It represents a variable voltage supply loaded from a real energy harvesting dataset
class HarvestingSupply(EnergySupply):
    def __init__(self, config, t_vector):
        profile = []
        sampling_period = config.get("sampling_period")
        filename = config.get("filename")
        if filename:
            profile = self._load_and_resample(
                filename, sampling_period, t_vector)
        else:
            profile = [random.uniform(0.0, 10.0)
                       for _ in range(len(t_vector))]

        self.type = config.get("type")
        self.voltage = 0.0
        self.profile = profile

    def _load_and_resample(self, filename, sampling_period, t_vector):
        with open(filename, "r") as f:
            raw = [float(line.strip()) for line in f if line.strip()]
        if not raw:
            return [0.0] * len(t_vector)
        result = []
        for t in t_vector:
            # Wrap around dataset if simulation is longer than the dataset
            raw_idx = (t / sampling_period) % len(raw)
            lo = int(raw_idx)
            hi = (lo + 1) % len(raw)
            frac = raw_idx - lo
            result.append(raw[lo] + frac * (raw[hi] - raw[lo]))
        return result

    def refresh(self, t_index):
        super().refresh(t_index)

    def print(self, t_index, file):
        super().print(t_index, file)
