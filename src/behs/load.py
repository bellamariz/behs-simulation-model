from abc import ABC, abstractmethod
import math


# Class Load for the BEHS simulation model
# It represents the load, a circuit component that consumes energy from the energy storage
class Load(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.v_on: float  # voltage threshold (V) for load to wake-up
        self.voltage: float  # voltage (V) across the load
        self.current: float  # current (A) flowing through the load
        self.energy_consumed: float  # energy consumed (J) by the load
        self.total_energy_consumed: float  # cumulative energy consumed (J)

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
    def calculate_energy_consumed(self, v_supply: float, t_step: float) -> float:
        pass

    # Refreshes the load's state based on 'v_supply' at each time step
    @abstractmethod
    def refresh(self, v_supply: float, t_step: float) -> None:
        self.voltage = self.calculate_voltage(v_supply)
        self.current = self.calculate_current(v_supply)
        self.energy_consumed = self.calculate_energy_consumed(v_supply, t_step)
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
    def __init__(self, config):
        self.RESISTANCE = config.get("resistance")
        self.P_RATING = config.get("p_rating")
        self.V_OPER = 1.8
        self.V_MAX = min(
            math.sqrt(self.P_RATING * self.RESISTANCE), config.get("v_max"))

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

    def calculate_energy_consumed(self, v_supply, t_step):
        if v_supply >= self.v_on:
            return (v_supply ** 2 / self.RESISTANCE) * t_step
        return 0.0

    def refresh(self, v_supply, t_step):
        super().refresh(v_supply, t_step)

    def print(self, t_index, file):
        super().print(t_index, file)


# Class MCU for the BEHS simulation model, inheriting from Load Class
# It represents a microcontroller unit (MCU), consuming energy based on its specs
class MCU(Load):
    def __init__(self, config):
        modes = config.get("modes")
        active_mode = modes.get("active")
        standby_mode = modes.get("standby")

        self.V_MIN = config.get("v_min")
        self.V_WAKE_UP = config.get("v_wake_up")
        self.V_OPER_STANDBY = standby_mode.get("v_oper")
        self.V_OPER_ACTIVE = active_mode.get("v_oper")
        self.V_MAX = config.get("v_max")
        self.ACTIVE_MODE = active_mode
        self.STANDBY_MODE = standby_mode

        self.type = config.get("type")
        self.v_on = self.V_WAKE_UP
        self.mode = "shutdown"  # "shutdown", "standby", "active"
        self.voltage = 0.0
        self.current = 0.0
        self.energy_consumed = 0.0
        self.total_energy_consumed = 0.0

    # TODO: Recalculate current (and energy) to include the cost from Program
    def calculate_current(self, v_supply):
        if self.mode == "active":
            return self.ACTIVE_MODE.get("cost")
        elif self.mode == "standby":
            return self.STANDBY_MODE.get("cost")
        else:
            return 0.0

    def calculate_voltage(self, v_supply):
        return v_supply if v_supply >= self.V_MIN else 0.0

    def calculate_energy_consumed(self, v_supply, t_step):
        return self.voltage * self.current * t_step

    # TODO: Update mode transitions to also include Program instructions
    def refresh(self, v_supply, t_step):
        super().refresh(v_supply, t_step)

        if v_supply < self.V_MIN:
            self.mode = "shutdown"
        elif v_supply >= self.V_WAKE_UP and v_supply < self.V_OPER_STANDBY:
            self.mode = "idle"
        elif v_supply >= self.V_OPER_STANDBY and v_supply < self.V_OPER_ACTIVE:
            self.mode = "standby"
        elif v_supply >= self.V_OPER_ACTIVE:
            self.mode = "active"

    def print(self, t_index, file):
        super().print(t_index, file)
