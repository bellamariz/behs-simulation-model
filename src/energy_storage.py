import math


class EnergyStorage:  # considering a simple RC circuit
    CAPACITANCE = 0.01
    RESISTANCE = 2500
    TIME_CONSTANT = CAPACITANCE * RESISTANCE

    def __init__(self, vmax, vin):
        self.max_voltage = vmax
        self.status = "empty"
        self.voltage = self.calculate_voltage(0, vin)
        self.current = self.calculate_current(0, vin)
        self.charge = self.calculate_charge(self.voltage)
        self.energy = self.calculate_charge(self.voltage)

    # Voltage across capacitor when charging, Vc(t), at instant t and given Vin (supply voltage)
    def calculate_charging_voltage(self, t, vin):
        return vin * (1 - math.exp(-t/self.TIME_CONSTANT))

    # Voltage across capacitor when discharging, Vc(t), at instant t
    # and given vci (capacitor initial voltage)
    def calculate_discharging_voltage(self, t, vci):
        return vci * math.exp(-t/self.TIME_CONSTANT)

    # Voltage across capacitor, Vc(t) at instant t
    def calculate_voltage(self, t, vin):
        if (self.status in ["charging", "empty"]):
            return self.calculate_charging_voltage(t, vin)
        if self.status == "discharging":
            return self.calculate_discharging_voltage(t, self.voltage)
        if self.status == "full":
            return self.max_voltage
        raise ValueError(f"unknown status: {self.status}")

    # Current flowing through the capacitor; V is Vin (charging) or Vci (discharging)
    def calculate_current(self, t, v):
        return (v / self.RESISTANCE) * math.exp(-t/self.TIME_CONSTANT)

    # Charge flowing through the capacitor, Q(t), at instant t and given Vc(t)
    def calculate_charge(self, vc):
        return self.CAPACITANCE * vc

    # Energy stored in capacitor, E(t), at instant t and given Vc(t)
    def calculate_energy(self, vc):
        return (1/2) * self.CAPACITANCE * (vc*vc)

    # Checks if capacitor is fully charged, i.e. Vc(t) reaches the maximum possible voltage
    def is_fully_charged(self):
        return self.voltage >= self.max_voltage

    # Given an instant t and supply voltage Vin, recalculate the stats for the Energy Storage
    def refresh_energy_storage(self, t, vin, status):
        self.status = status
        self.voltage = self.calculate_voltage(t, vin)
        self.current = self.calculate_current(t, vin)
        self.charge = self.calculate_charge(self.voltage)
        self.energy = self.calculate_energy(self.voltage)

    def print(self, t):
        print(
            f"t={t},"
            f"status={self.status},"
            f"voltage={self.voltage:.5f}V,"
            f"current={self.current:.5f}A,"
            f"charge={self.charge:.5f}C,"
            f"energy={self.energy:.5f}J\n"
        )
