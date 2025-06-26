import math
from abc import ABC, abstractmethod

# v_supply is provided by the energy supply (e.g. constant, harvester, etc)


class EnergyStorage(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.voltage: float
        self.current: float
        self.energy: float

    @abstractmethod
    def calculate_voltage(self, t_time: int, v_supply: float) -> float:
        pass

    @abstractmethod
    def calculate_current(self, t_time: int, v_supply: float) -> float:
        pass

    @abstractmethod
    def calculate_energy_stored(self) -> float:
        pass

    @abstractmethod
    def refresh(self, t_time: float, v_supply: float) -> None:
        self.voltage = self.calculate_voltage(t_time, v_supply)
        self.current = self.calculate_current(t_time, v_supply)
        self.energy = self.calculate_energy_stored()

    @abstractmethod
    def print(self, t_index: int) -> None:
        print(
            f"Energy Storage: {self.type} --> "
            f"t={t_index},"
            f"voltage={self.voltage:.5f}V,"
            f"current={self.current:.5f}A,"
            f"energy_stored={self.energy:.5f}J\n"
        )
        pass


class Capacitor(EnergyStorage):
    CAPACITANCE = 0.01
    RESISTANCE = 2500
    TIME_CONSTANT = CAPACITANCE * RESISTANCE
    V_STORAGE_MAX = 10.0  # maximum capacity of energy storage
    V_LOAD_MIN = 5.0  # minimum voltage for supplying load

    def __init__(self):
        self.type = "capacitor"
        self.voltage = 0.0
        self.current = 0.0
        self.energy = 0.0

        # Voltage across capacitor when charging, Vc(t), at instant t and given Vin (supply voltage)
    def charging_voltage(self, t_time, v_supply):
        return v_supply * (1 - math.exp(-t_time/self.TIME_CONSTANT))

    # Voltage across capacitor when discharging, Vc(t), at instant t
    # and given vci (capacitor initial voltage)
    def discharging_voltage(self, t_time, v_supply):
        return v_supply * math.exp(-t_time/self.TIME_CONSTANT)

    # Voltage across capacitor, Vc(t) at instant t
    def calculate_voltage(self, t_time, v_supply):
        if self.voltage >= self.V_STORAGE_MAX:
            print(
                f"Energy storage is at maximum capacity {self.V_STORAGE_MAX}V")
            return self.V_STORAGE_MAX
        elif self.voltage < self.V_STORAGE_MAX:
            # capacitor is charging
            if self.voltage <= self.V_LOAD_MIN:
                return self.charging_voltage(t_time, v_supply)
            # capacitor is discharging
            elif self.voltage > self.V_LOAD_MIN:
                return self.discharging_voltage(t_time, v_supply)

    # Current flowing through the capacitor; V is Vin (charging) or Vci (discharging)
    def calculate_current(self, t_time, v_supply):
        # capacitor is charging
        if self.voltage <= self.V_LOAD_MIN:
            return (v_supply / self.RESISTANCE) * math.exp(-t_time/self.TIME_CONSTANT)
        # capacitor is discharging
        elif self.voltage > self.V_LOAD_MIN:
            return (self.voltage / self.RESISTANCE) * math.exp(-t_time/self.TIME_CONSTANT)

    # Energy stored in capacitor, E(t), at instant t and given Vc(t)
    def calculate_energy_stored(self):
        return (1/2) * self.CAPACITANCE * (self.voltage*self.voltage)

    # Given an instant t and supply voltage Vin, recalculate the stats for the Energy Storage
    def refresh(self, t_time, v_supply):
        super().refresh(t_time, v_supply)

    def print(self, t_index):
        super().print(t_index)
