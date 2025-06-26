from abc import ABC, abstractmethod

# v_supply is provided by the energy storage (e.g. capacitor, etc)


class Load(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.operating_voltage: float
        self.voltage: float
        self.current: float
        self.energy_consumed: float

    @abstractmethod
    def calculate_voltage(self, v_supply: float) -> float:
        pass

    @abstractmethod
    def calculate_current(self, v_supply: float) -> float:
        pass

    @abstractmethod
    def calculate_energy_consumed(self, v_supply: float) -> float:
        pass

    @abstractmethod
    def refresh(self, v_supply: float) -> None:
        self.voltage = self.calculate_voltage(v_supply)
        self.current = self.calculate_current(v_supply)
        self.energy_consumed = self.calculate_energy_consumed(v_supply)

    @abstractmethod
    def print(self, t_index: int) -> None:
        print(
            f"Load: {self.type} --> "
            f"t={t_index},"
            f"operating_voltage={self.operating_voltage:.5f}V,"
            f"voltage={self.voltage:.5f}V,"
            f"current={self.current:.5f}A,"
            f"energy_consumed={self.energy_consumed:.5f}J\n"
        )
        pass


class Resistor(Load):
    ENERGY_CONSUMPTION = 0.001  # in joules, assumed constant
    OPERATING_VOLTAGE = 1.0  # in volts, minimum for operation
    RESISTANCE = 1000

    def __init__(self):
        self.type = "resistor"
        self.operating_voltage = self.OPERATING_VOLTAGE
        self.voltage = 0.0  # in volts
        self.current = 0.0  # in amperes
        self.energy_consumed = 0.0  # in joules

    def calculate_current(self, v_supply):
        if v_supply >= self.operating_voltage:
            return v_supply / self.RESISTANCE
        return 0.0

    def calculate_voltage(self, v_supply):
        if v_supply >= self.operating_voltage:
            return v_supply
        return 0.0

    def calculate_energy_consumed(self, v_supply):
        if v_supply >= self.operating_voltage:
            return self.ENERGY_CONSUMPTION
        return 0.0


class MCU(Load):
    ENERGY_CONSUMPTION = 0.02  # in joules, assumed constant
    OPERATING_VOLTAGE = 3.3  # in volts, minimum for operation
    OPERATING_CURRENT = 0.002  # in amperes, assumed constant

    def __init__(self):
        self.type = "mcu"
        self.operating_voltage = self.OPERATING_VOLTAGE
        self.voltage = 0.0  # in volts
        self.current = 0.0  # in amperes
        self.energy_consumed = 0.0  # in joules

    def calculate_current(self, v_supply):
        if v_supply >= self.operating_voltage:
            return self.OPERATING_CURRENT
        return 0.0

    def calculate_voltage(self, v_supply):
        if v_supply >= self.operating_voltage:
            return self.OPERATING_VOLTAGE
        return 0.0

    def calculate_energy_consumed(self, v_supply):
        if v_supply >= self.operating_voltage:
            return self.ENERGY_CONSUMPTION
        return 0.0
