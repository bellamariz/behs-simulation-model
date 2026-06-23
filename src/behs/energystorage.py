import math
from abc import ABC, abstractmethod


# Class EnergyStorage for the BEHS simulation model
# It represents the energy storage, a circuit component that stores energy for later use.
class EnergyStorage(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.status: str
        self.voltage: float        # voltage (V) across the storage at time t
        self.current: float        # current (A) through the storage at time t
        self.energy_stored: float  # energy stored (J) in the buffer at time t
        self.power_stored: float   # power stored (W) at time t

    # Calculates the voltage across the storage, derived from the energy stored
    @abstractmethod
    def calculate_voltage(self) -> float:
        pass

    # Calculates the current flowing through the storage, derived from power and voltage
    @abstractmethod
    def calculate_current(self) -> float:
        pass

    # Calculates the energy stored
    @abstractmethod
    def calculate_energy_stored(self, e_supply: float, e_load: float) -> float:
        pass

    # Calculates the power stored
    @abstractmethod
    def calculate_power_stored(self, t_step: float) -> float:
        pass

    # Refreshes the energy storage's state at each time step
    # Depends on the energy supply and energy consumed by the load
    @abstractmethod
    def refresh(self, e_supply: float, e_load: float, t_step: float) -> None:
        self.energy_stored = self.calculate_energy_stored(
            e_supply, e_load)
        self.voltage = self.calculate_voltage()
        self.power_stored = self.calculate_power_stored(t_step)
        self.current = self.calculate_current()

    # Prints the energy storage's state at a given time index
    @abstractmethod
    def print(self, t_index: int, file) -> None:
        print(
            f"Energy Storage: {self.type} --> "
            f"t={t_index},"
            f"status={self.status},"
            f"voltage={self.voltage:.5f}V,"
            f"current={self.current:.5f}A,"
            f"energy_stored={self.energy_stored:.5f}J,"
            f"power_stored={self.power_stored:.5f}W",
            file=file
        )


# Class Capacitor for the BEHS simulation model, inheriting from EnergyStorage Class
# It represents a capacitor, estimating its energy from load consumption and energy supply.
#   E(t) = E(t-1) + Esupply(t) - Eload(t)
#   V(t) = sqrt(2 * E(t) / C)
class Capacitor(EnergyStorage):
    def __init__(self, config):
        self.CAPACITANCE = config.get("capacitance")
        self.V_MAX = config.get("v_oper_max")
        self.E_MAX = 0.5 * self.CAPACITANCE * self.V_MAX ** 2

        self.type = config.get("type")
        self.status = "idle"
        self.voltage = 0.0
        self.current = 0.0
        self.energy_stored = 0.0
        self.power_stored = 0.0

    # Voltage is estimated from energy stored: V(t) = sqrt(2 * E(t) / C)
    def calculate_voltage(self):
        return math.sqrt(2 * self.energy_stored / self.CAPACITANCE) if self.energy_stored > 0 else 0.0

    # Current is estimated from power and voltage: I(t) = P(t) / V(t)
    def calculate_current(self):
        return (self.power_stored / self.voltage) if self.voltage > 0 else 0.0

    # Energy stored in capacitor: E(t) = E(t-1) + Esupply(t) - Eload(t)
    def calculate_energy_stored(self, e_supply, e_load):
        energy = self.energy_stored + e_supply - e_load
        return min(energy, self.E_MAX) if energy > 0 else 0.0

    # Available power from storage: P(t) = E(t) / t_step
    # Represents the maximum power the capacitor could deliver given its current stored energy.
    def calculate_power_stored(self, t_step):
        return self.energy_stored / t_step if self.energy_stored > 0 else 0.0

    def refresh(self, e_supply: float, e_load: float, t_step: float) -> None:
        super().refresh(e_supply, e_load, t_step)

        delta_energy = e_supply - e_load
        if self.energy_stored >= self.E_MAX:
            self.status = "full"
        elif self.energy_stored <= 0:
            self.status = "empty"
        elif delta_energy > 0:
            self.status = "charging"
        elif delta_energy < 0:
            self.status = "discharging"
        else:
            self.status = "idle"

    def print(self, t_index, file):
        super().print(t_index, file)
