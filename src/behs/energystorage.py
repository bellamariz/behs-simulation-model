import math
from abc import ABC, abstractmethod


# Class EnergyStorage for the BEHS simulation model
# It represents the energy storage, a circuit component that stores energy for later use
class EnergyStorage(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.status: str
        self.voltage: float  # voltage across the energy storage, in Voltz
        self.current: float  # current flowing through the energy storage, in Amperes
        self.energy_stored: float  # energy stored by the buffer, in Joules

    # Calculates the voltage across the storage based on 'v_supply'
    # Param 'v_supply' is provided by the energy supply (e.g. constant, harvester, etc)

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

    # Refreshes the storage's state based on 'v_supply' and 'load_energy_consumed'
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
            f"status={self.status},"
            f"voltage={self.voltage:.5f}V,"
            f"current={self.current:.5f}A,"
            f"energy_stored={self.energy_stored:.5f}J",
            file=file
        )


# Class Capacitor for the BEHS simulation model, inheriting from EnergyStorage Class
# It represents a capacitor, with its equations considering a RC circuit model
class Capacitor(EnergyStorage):
    def __init__(self, config, v_load_min, v_load_max):
        self.CAPACITANCE = config.get("capacitance")
        self.R_SERIES = config.get("r_charge")
        self.V_MAX = config.get("v_oper_max")
        self.V_LOAD_MIN = v_load_min
        self.V_LOAD_MAX = v_load_max
        self.TIME_CONSTANT = self.CAPACITANCE * self.R_SERIES

        self.type = config.get("type")
        self.status = "idle"  # "charging", "ready", "discharging" or "idle"
        self.voltage = 0.0
        self.current = 0.0
        self.energy_stored = 0.0
        self.t_ref = 0
        self.v_discharge_init = 0.0
        self.v_charge_init = 0.0

    # Voltage across capacitor when charging, Vc(t), at instant t and given Vin (supply voltage)
    def charging_voltage(self, t_time, v_supply):
        return v_supply + (self.v_charge_init - v_supply) * math.exp(-t_time/self.TIME_CONSTANT)

    # Voltage across capacitor when discharging, Vc(t), at instant t
    def discharging_voltage(self, t_time):
        return self.v_discharge_init * math.exp(-t_time/self.TIME_CONSTANT)

    # Voltage across capacitor, Vc(t) at instant t
    def calculate_voltage(self, t_time, v_supply):
        if self.status == "idle":
            self.status = "charging"
            self.t_ref = t_time
            self.v_charge_init = self.voltage
            return self.voltage

        elapsed = t_time - self.t_ref

        if self.status == "charging":
            if self.voltage >= self.V_LOAD_MAX or self.voltage >= self.V_MAX:
                self.status = "ready"
                return min(self.V_LOAD_MAX, self.V_MAX)
            return self.charging_voltage(elapsed, v_supply)

        if self.status == "ready":
            self.t_ref = t_time
            self.v_discharge_init = self.voltage
            self.status = "discharging"
            return self.voltage

        if self.status == "discharging":
            if self.voltage <= self.V_LOAD_MIN:
                self.status = "idle"
                return self.voltage
            return self.discharging_voltage(elapsed)

    # Current flowing through the capacitor; V is Vin (charging) or Vci (discharging)
    def calculate_current(self, t_time, v_supply):
        if self.status == "idle":
            return 0.0

        elapsed = t_time - self.t_ref

        if self.status == "charging":
            return ((v_supply - self.v_charge_init) / self.R_SERIES) * math.exp(-elapsed/self.TIME_CONSTANT)

        if self.status == "discharging":
            return (self.v_discharge_init / self.R_SERIES) * math.exp(-elapsed/self.TIME_CONSTANT)

        if self.status == "ready":
            return 0.0

    # Energy stored in capacitor, E(t), at instant t and given Vc(t)
    def calculate_energy_stored(self, load_energy_consumed):
        energy = (1/2) * self.CAPACITANCE * (self.voltage*self.voltage)
        if self.status == "discharging":
            return energy - load_energy_consumed
        return energy

    def refresh(self, t_time, v_supply, load_energy_consumed):
        super().refresh(t_time, v_supply, load_energy_consumed)

    def print(self, t_index, file):
        super().print(t_index, file)
