from abc import ABC, abstractmethod
import math

from src.program.program import Program


# Class Load for the BEHS simulation model
# It represents the load, a circuit component that consumes energy from the energy storage
class Load(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.mode: str  # operational mode (e.g., active, standby, shutdown)
        self.v_on: float  # voltage threshold (V) for load to wake-up
        self.voltage: float  # voltage (V) across the load
        self.current: float  # current (A) flowing through the load
        self.energy_consumed: float  # energy consumed (J) by the load
        self.total_energy_consumed: float  # cumulative energy consumed (J)
        self.program: Program  # software executed by load (if applicable)

    # Param 'v_supply' is the current voltage supplied by the energy storage

    # Calculates the voltage across the load based on 'v_supply'
    @abstractmethod
    def calculate_voltage(self, v_supply: float) -> float:
        pass

    # Calculates the current flowing through the load based on 'v_supply'
    @abstractmethod
    def calculate_current(self, v_supply: float, t_step: float) -> float:
        pass

    # Calculates the energy consumed by the load based on 'v_supply'
    @abstractmethod
    def calculate_energy_consumed(self, v_supply: float, t_step: float) -> float:
        pass

    # Load Program from the configuration
    @abstractmethod
    def upload_software(self, program: Program) -> None:
        self.program = program

    # Refreshes the load's state based on 'v_supply' at each time step
    @abstractmethod
    def refresh(self, v_supply: float, t_step: float) -> None:
        self.voltage = self.calculate_voltage(v_supply)
        self.current = self.calculate_current(v_supply, t_step)
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
# It represents a resistor, a Load that consumes constant energy
class Resistor(Load):
    def __init__(self, config):
        # Class specific attributes
        self.RESISTANCE = config.get("resistance")
        self.P_RATING = config.get("p_rating")
        self.V_OPER = 1.8
        self.V_MAX = min(
            math.sqrt(self.P_RATING * self.RESISTANCE), config.get("v_max"))

        # Inherited attributes
        self.type = config.get("type")
        self.mode = "on"
        self.v_on = min(self.V_OPER, self.V_MAX)
        self.voltage = 0.0
        self.current = 0.0
        self.energy_consumed = 0.0
        self.total_energy_consumed = 0.0
        self.program = None

    # If supply voltage exceeds V_MAX, we assume the Load stays at V_MAX
    # We assume there is a voltage regulator between the EnergyStorage and Load
    def calculate_voltage(self, v_supply):
        if v_supply < self.v_on:
            return 0.0
        return min(v_supply, self.V_MAX)

    def calculate_current(self, v_supply, t_step):
        if v_supply >= self.v_on:
            return min(v_supply, self.V_MAX) / self.RESISTANCE
        return 0.0

    def calculate_energy_consumed(self, v_supply, t_step):
        if v_supply >= self.v_on:
            v = min(v_supply, self.V_MAX)
            return (v ** 2 / self.RESISTANCE) * t_step
        return 0.0

    def upload_software(self, program):
        super().upload_software(program)

    def refresh(self, v_supply, t_step):
        super().refresh(v_supply, t_step)

    def print(self, t_index, file):
        super().print(t_index, file)


# Class MCU for the BEHS simulation model, inheriting from Load Class
# It represents a microcontroller unit (MCU), a Load that consumes variable energy.
class MCU(Load):
    def __init__(self, config):
        modes = config.get("modes")

        # Class specific attributes
        self.ACTIVE_MODE = modes.get("active")
        self.STANDBY_MODE = modes.get("standby")
        self.SHUTDOWN_MODE = modes.get("shutdown")
        self.V_MIN = config.get("v_min")
        self.V_MAX = config.get("v_max")
        self.V_OPER_SHUTDOWN = self.SHUTDOWN_MODE.get("v_oper")
        self.V_OPER_STANDBY = self.STANDBY_MODE.get("v_oper")
        self.V_OPER_ACTIVE = self.ACTIVE_MODE.get("v_oper")

        # Inherited attributes
        self.type = config.get("type")
        self.mode = "off"
        self.v_on = self.V_MIN
        self.voltage = 0.0
        self.current = 0.0
        self.energy_consumed = 0.0
        self.total_energy_consumed = 0.0
        self.program = None

    # If supply voltage exceeds V_MAX, we assume the Load stays at V_MAX
    # We assume there is a voltage regulator between the EnergyStorage and Load
    def calculate_voltage(self, v_supply):
        if v_supply < self.V_MIN:
            return 0.0
        return min(v_supply, self.V_MAX)

    def calculate_current(self, v_supply, t_step):
        # We only execute the program if the MCU is in active mode
        if self.mode == "active":
            active_cost = self.ACTIVE_MODE.get("cost")
            if self.program is not None:
                op = self.program.get_executing_operation()
                if op is not None:
                    return active_cost + op.get_cost_for_t_step(t_step)
            return active_cost
        elif self.mode == "standby":
            return self.STANDBY_MODE.get("cost")
        elif self.mode == "shutdown":
            return self.SHUTDOWN_MODE.get("cost")
        else:
            return 0.0

    def calculate_energy_consumed(self, v_supply, t_step):
        return self.voltage * self.current * t_step

    def upload_software(self, program):
        super().upload_software(program)

    def refresh(self, v_supply, t_step):
        # Update mode before calculating energy so costs reflect current state
        if v_supply < self.V_MIN:
            self.mode = "off"
        elif self.V_MIN <= v_supply < self.V_OPER_SHUTDOWN:
            self.mode = "idle"
        elif self.V_OPER_SHUTDOWN <= v_supply < self.V_OPER_STANDBY:
            self.mode = "shutdown"
        elif self.V_OPER_STANDBY <= v_supply < self.V_OPER_ACTIVE:
            self.mode = "standby"
        elif v_supply >= self.V_OPER_ACTIVE:
            self.mode = "active"

        # Update Load state
        super().refresh(v_supply, t_step)

        # Advance program counter after energy is calculated for time step
        if self.mode == "active" and self.program is not None:
            self.program.t_steps_completed += 1

    def print(self, t_index, file):
        super().print(t_index, file)
