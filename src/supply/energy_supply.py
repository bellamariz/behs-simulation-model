import random

# There are three energy supply profiles:
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

from abc import ABC, abstractmethod


class EnergySupply(ABC):
    MAX_SUPPLY_VOLTAGE = 10  # assumes max supply voltage of 10V

    @abstractmethod
    def __init__(self):
        self.type: str
        self.voltage: float
        self.profile: list[float]

    @abstractmethod
    def refresh(self, t_index: int) -> None:
        self.voltage = self.profile[t_index]

    @abstractmethod
    def print(self, t_index: int) -> None:
        print(
            f"Energy Supply: {self.type} --> "
            f"t={t_index},"
            f"voltage={self.voltage:.5f}V\n"
        )


class ConstantSupply(EnergySupply):
    def __init__(self, t_vector):
        self.type = "constant"
        self.voltage = 0.0
        self.profile = [8.0] * len(t_vector)

    def refresh(self, t_index):
        super().refresh(t_index)

    def print(self, t_index):
        super().print(t_index)


class HarvestingSupply(EnergySupply):
    def __init__(self, t_vector):
        self.type = "harvesting"
        self.voltage = 0.0
        self.profile = [random.uniform(0.0, self.MAX_SUPPLY_VOLTAGE)
                        for _ in range(len(t_vector))]

    def refresh(self, t_index):
        super().refresh(t_index)

    def print(self, t_index):
        super().print(t_index)
