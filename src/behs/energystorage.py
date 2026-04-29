import math
from abc import ABC, abstractmethod


# Class EnergyStorage for the BEHS simulation model
# It represents the energy storage, a circuit component that stores energy for later use
class EnergyStorage(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.voltage: float  # voltage across the energy storage, in Voltz
        self.current: float  # current flowing through the energy storage, in Amperes
        self.energy_stored: float  # energy stored by the buffer, in Joules

    # Param 'v_supply' is provided by the energy supply (e.g. constant, harvester, etc)

    # Calculates the voltage across the storage based on 'v_supply'
    @abstractmethod
    def calculate_voltage(self, t_time: int, v_supply: float) -> float:
        pass

    # Calculates the current flowing through the storage based on 'v_supply'
    @abstractmethod
    def calculate_current(self, t_time: int, v_supply: float) -> float:
        pass

    # Calculates the energy stored, discounted by the energy consumed by the load
    @abstractmethod
    def calculate_energy_stored(self, load_energy_consumed: float) -> float:
        pass

    # Refreshes the storage's state based on 'v_supply' and 'v_load_min'
    @abstractmethod
    def refresh(self, t_time: float, v_supply: float, load_energy_consumed: float) -> None:
        self.voltage = self.calculate_voltage(t_time, v_supply)
        self.current = self.calculate_current(t_time, v_supply)
        self.energy_stored = self.calculate_energy_stored(load_energy_consumed)

    # Prints the storage's state at a given time index
    @abstractmethod
    def print(self, t_index: int, file) -> None:
        print(
            f"Energy Storage: {self.type} --> "
            f"t={t_index},"
            f"voltage={self.voltage:.5f}V,"
            f"current={self.current:.5f}A,"
            f"energy_stored={self.energy_stored:.5f}J",
            file=file
        )


# Class Capacitor for the BEHS simulation model, inheriting from EnergyStorage Class
# It represents a capacitor, with its equations considering a RC circuit model
class Capacitor(EnergyStorage):
    CAPACITANCE = 0.01
    RESISTANCE = 2500
    TIME_CONSTANT = CAPACITANCE * RESISTANCE
    V_STORAGE_MAX = 10.0  # maximum capacity of energy storage
    V_LOAD_MIN = 4.0  # minimum voltage needed for supplying load

    def __init__(self):
        self.type = "capacitor"
        self.voltage = 0.0
        self.current = 0.0
        self.energy = 0.0

    # Voltage across capacitor when charging, Vc(t), at instant t and given Vin (supply voltage)
    def charging_voltage(self, t_time, v_supply):
        return v_supply * (1 - math.exp(-t_time/self.TIME_CONSTANT))

    # Voltage across capacitor when discharging, Vc(t), at instant t
    def discharging_voltage(self, t_time):
        return self.voltage * math.exp(-t_time/self.TIME_CONSTANT)

    # Voltage across capacitor, Vc(t) at instant t
    def calculate_voltage(self, t_time, v_supply):
        if self.voltage <= self.V_STORAGE_MAX:
            # capacitor is charging
            if self.voltage <= self.V_LOAD_MIN:
                return self.charging_voltage(t_time, v_supply)
            # capacitor is discharging
            if self.voltage > self.V_LOAD_MIN:
                return self.voltage - self.discharging_voltage(t_time)
        print(f"Energy storage is at maximum capacity {self.V_STORAGE_MAX}V")
        return self.V_STORAGE_MAX

    # Current flowing through the capacitor; V is Vin (charging) or Vci (discharging)
    def calculate_current(self, t_time, v_supply):
        # capacitor is charging
        if self.voltage <= self.V_LOAD_MIN:
            return (v_supply / self.RESISTANCE) * math.exp(-t_time/self.TIME_CONSTANT)
        # capacitor is discharging
        return (self.voltage / self.RESISTANCE) * math.exp(-t_time/self.TIME_CONSTANT)

    # Energy stored in capacitor, E(t), at instant t and given Vc(t)
    def calculate_energy_stored(self, load_energy_consumed):
        energy = (1/2) * self.CAPACITANCE * (self.voltage*self.voltage)
        # capacitor is charging
        if self.voltage <= self.V_LOAD_MIN:
            return energy
        # capacitor is discharging
        return energy - load_energy_consumed

    def refresh(self, t_time, v_supply, load_energy_consumed):
        super().refresh(t_time, v_supply, load_energy_consumed)

    def print(self, t_index, file):
        super().print(t_index, file)
