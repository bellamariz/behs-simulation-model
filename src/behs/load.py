from abc import ABC, abstractmethod
import math

from LoadSimulator import config


# Class Load for the BEHS simulation model
# It represents the load, a circuit component that consumes energy from the energy storage
class Load(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.v_on: float  # voltage threshold for load to wake-up
        self.voltage: float  # voltage across the load, in Voltz
        self.current: float  # current flowing through the load, in Amperes
        self.energy_consumed: float  # energy consumed by the load, in Joules
        self.total_energy_consumed: float  # cumulative energy consumed, in Joules

    # Param 'v_supply' is the current voltage supplied by the energy storage

    # Calculates the voltage across the load based on 'v_supply'
    @abstractmethod
    def calculate_voltage(self, v_supply: float) -> float:
        pass

    # Calculates the current flowing through the load based on 'v_supply'
    @abstractmethod
    def calculate_current(self, v_supply: float) -> float:
        pass

    # Calculates the energy consumed by the load based on 'v_supply'
    @abstractmethod
    def calculate_energy_consumed(self, v_supply: float) -> float:
        pass

    # Refreshes the load's state based on 'v_supply'
    @abstractmethod
    def refresh(self, v_supply: float) -> None:
        self.voltage = self.calculate_voltage(v_supply)
        self.current = self.calculate_current(v_supply)
        self.energy_consumed = self.calculate_energy_consumed(v_supply)
        self.total_energy_consumed += self.energy_consumed

    # Prints the load's state at a given time index
    @abstractmethod
    def print(self, t_index: int, file) -> None:
        print(
            f"Load: {self.type} --> "
            f"t={t_index},"
            f"v_on={self.v_on:.5f}V,"
            f"voltage={self.voltage:.5f}V,"
            f"current={self.current:.5f}A,"
            f"energy_consumed={self.energy_consumed:.5f}J,"
            f"total_energy_consumed={self.total_energy_consumed:.5f}J",
            file=file
        )


# Class Resistor for the BEHS simulation model, inheriting from Load Class
# It represents a resistor, consuming energy based on its resistance
class Resistor(Load):
    def __init__(self, config, t_step):
        self.RESISTANCE = config.get("resistance")
        self.P_RATING = config.get("p_rating")
        self.V_MAX = math.sqrt(self.P_RATING * self.RESISTANCE)
        self.V_OPER = 1.8
        self.T_STEP = t_step

        self.type = config.get("type")
        self.v_on = min(self.V_OPER, self.V_MAX)
        self.voltage = 0.0
        self.current = 0.0
        self.energy_consumed = 0.0
        self.total_energy_consumed = 0.0

    def calculate_current(self, v_supply):
        if v_supply >= self.v_on:
            return v_supply / self.RESISTANCE
        return 0.0

    def calculate_voltage(self, v_supply):
        if v_supply >= self.v_on:
            return v_supply
        return 0.0

    def calculate_energy_consumed(self, v_supply):
        if v_supply >= self.v_on:
            return self.P_RATING * self.T_STEP
        return 0.0

    def refresh(self, v_supply):
        super().refresh(v_supply)

    def print(self, t_index, file):
        super().print(t_index, file)


# Class MCU for the BEHS simulation model, inheriting from Load Class
# It represents a microcontroller unit (MCU), consuming energy based on its specs
class MCU(Load):
    def __init__(self, config, t_step):
        self.V_MIN = config.get("v_min")
        self.V_WAKE_UP = config.get("v_wake_up")
        self.V_OPER_LOW = config.get("v_oper_low")
        self.V_OPER_ACTIVE = config.get("v_oper_active")
        self.V_MAX = config.get("v_max")
        self.MODES = config.get("modes")
        self.PROGRAM_FILE = config.get("program")
        self.T_STEP = t_step

        self.type = config.get("type")
        self.v_on = self.V_WAKE_UP
        self.mode = "shutdown"  # "shutdown", "low_power", "active"
        self.voltage = 0.0
        self.current = 0.0
        self.energy_consumed = 0.0
        self.total_energy_consumed = 0.0

    def calculate_current(self, v_supply):
        if self.mode == "active":
            return self.MODES.get("active")
        elif self.mode == "low_power":
            return self.MODES.get("low_power")
        else:
            return self.MODES.get("shutdown", 0.0)

    def calculate_voltage(self, v_supply):
        return v_supply if v_supply >= self.V_MIN else 0.0

    def calculate_energy_consumed(self, v_supply):
        return self.calculate_voltage(v_supply) * self.calculate_current(v_supply) * self.T_STEP

    def refresh(self, v_supply):
        if v_supply > self.V_MAX:
            self.mode = "shutdown"
            raise ValueError(
                f"Supply voltage {v_supply:.5f}V exceeds the resistor's power rating {self.V_MAX:.5f}V!")

        if v_supply <= self.V_MIN:
            self.mode = "shutdown"
        elif v_supply >= self.V_OPER_LOW and v_supply < self.V_OPER_ACTIVE:
            self.mode = "low_power"
        elif v_supply >= self.V_OPER_ACTIVE:
            self.mode = "active"

        super().refresh(v_supply)

    def print(self, t_index, file):
        super().print(t_index, file)
