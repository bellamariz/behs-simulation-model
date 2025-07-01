from abc import ABC, abstractmethod


# Class Load for the BEHS simulation model
# It represents the load, a circuit component that consumes energy from the energy storage
class Load(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.operating_voltage: float  # minimum voltage required for operation
        self.voltage: float  # voltage across the load, in Voltz
        self.current: float  # current flowing through the load, in Amperes
        self.energy_consumed: float  # energy consumed by the load, in Joules
        self.total_energy_consumed: float  # cumulative energy consumed, in Joules

    # Param 'v_supply' is the current voltage supplied by the energy storage
    # Param 'v_load_min' is the min voltage needed for energy storage to start supplying load

    # Calculates the voltage across the load based on 'v_supply'
    @abstractmethod
    def calculate_voltage(self, v_supply: float, v_load_min: float) -> float:
        pass

    # Calculates the current flowing through the load based on 'v_supply'
    @abstractmethod
    def calculate_current(self, v_supply: float, v_load_min: float) -> float:
        pass

    # Calculates the energy consumed by the load based on 'v_supply'
    @abstractmethod
    def calculate_energy_consumed(self, v_supply: float, v_load_min: float) -> float:
        pass

    # Refreshes the load's state based on 'v_supply' and 'v_load_min'
    @abstractmethod
    def refresh(self, v_supply: float, v_load_min: float) -> None:
        self.voltage = self.calculate_voltage(v_supply, v_load_min)
        self.current = self.calculate_current(v_supply, v_load_min)
        self.energy_consumed = self.calculate_energy_consumed(
            v_supply, v_load_min)
        self.total_energy_consumed += self.calculate_energy_consumed(
            v_supply, v_load_min)

    # Prints the load's state at a given time index
    @abstractmethod
    def print(self, t_index: int, file) -> None:
        print(
            f"Load: {self.type} --> "
            f"t={t_index},"
            f"operating_voltage={self.operating_voltage:.5f}V,"
            f"voltage={self.voltage:.5f}V,"
            f"current={self.current:.5f}A,"
            f"energy_consumed={self.energy_consumed:.5f}J,"
            f"total_energy_consumed={self.total_energy_consumed:.5f}J",
            file=file
        )


# Class Resistor for the BEHS simulation model, inheriting from Load Class
# It represents a resistor, consuming energy based on its resistance
class Resistor(Load):
    ENERGY_CONSUMPTION = 0.001  # Assumed constant for simplicity
    OPERATING_VOLTAGE = 1.0  # Minimum operating voltage
    RESISTANCE = 1000

    def __init__(self):
        self.type = "resistor"
        self.operating_voltage = self.OPERATING_VOLTAGE
        self.voltage = 0.0
        self.current = 0.0
        self.energy_consumed = 0.0
        self.total_energy_consumed = 0.0

    def calculate_current(self, v_supply, v_load_min):
        if (v_supply >= self.operating_voltage) and (v_supply >= v_load_min):
            return v_supply / self.RESISTANCE
        return 0.0

    def calculate_voltage(self, v_supply, v_load_min):
        if (v_supply >= self.operating_voltage) and (v_supply >= v_load_min):
            return v_supply
        return 0.0

    def calculate_energy_consumed(self, v_supply, v_load_min):
        if (v_supply >= self.operating_voltage) and (v_supply >= v_load_min):
            return self.ENERGY_CONSUMPTION
        return 0.0

    def refresh(self, v_supply, v_load_min):
        super().refresh(v_supply, v_load_min)

    def print(self, t_index, file):
        super().print(t_index, file)


# Class Load for the BEHS simulation model, inheriting from Load Class
# It represents a microcontroller unit (MCU), consuming energy based on its specs
class MCU(Load):
    # Values assumed constant for simplicity
    ENERGY_CONSUMPTION = 0.02
    OPERATING_VOLTAGE = 3.3
    OPERATING_CURRENT = 0.002

    def __init__(self):
        self.type = "mcu"
        self.operating_voltage = self.OPERATING_VOLTAGE
        self.voltage = 0.0  # in volts
        self.current = 0.0  # in amperes
        self.energy_consumed = 0.0  # in joules
        self.total_energy_consumed = 0.0  # in joules, cumulative energy consumed

    def calculate_current(self, v_supply, v_load_min):
        if (v_supply >= self.operating_voltage) and (v_supply >= v_load_min):
            return self.OPERATING_CURRENT
        return 0.0

    def calculate_voltage(self, v_supply, v_load_min):
        if (v_supply >= self.operating_voltage) and (v_supply >= v_load_min):
            return self.OPERATING_VOLTAGE
        return 0.0

    def calculate_energy_consumed(self, v_supply, v_load_min):
        if (v_supply >= self.operating_voltage) and (v_supply >= v_load_min):
            return self.ENERGY_CONSUMPTION
        return 0.0

    def refresh(self, v_supply, v_load_min):
        super().refresh(v_supply, v_load_min)

    def print(self, t_index, file):
        super().print(t_index, file)
