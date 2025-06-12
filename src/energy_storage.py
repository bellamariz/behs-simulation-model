import math


class EnergyStorage:  # considering a simple RC circuit
    CAPACITANCE = 0.01
    RESISTANCE = 2500
    TIME_CONSTANT = CAPACITANCE * RESISTANCE

    def __init__(self, Vmax, Vin):
        self.max_voltage = Vmax
        self.status = "empty"
        self.voltage = self.calculate_voltage(0, Vin)
        self.current = self.calculate_current(0, Vin)
        self.charge = self.calculate_charge(self.voltage)
        self.energy = self.calculate_charge(self.voltage)

    # Voltage across capacitor when charging, Vc(t), at instant t and given Vin (supply voltage)
    def calculate_charging_voltage(self, t, Vin):
        return Vin * (1 - math.exp(-t/self.TIME_CONSTANT))

    # Voltage across capacitor when discharging, Vc(t), at instant t and given Vci (capacitor initial voltage)
    def calculate_discharging_voltage(self, t, Vci):
        return Vci * math.exp(-t/self.TIME_CONSTANT)

    # Voltage across capacitor, Vc(t) at instant t
    def calculate_voltage(self, t, Vin):
        if (self.status == "charging") or (self.status == "empty"):
            return self.calculate_charging_voltage(t, Vin)
        elif self.status == "discharging":
            return self.calculate_discharging_voltage(t, self.voltage)
        elif self.status == "full":
            return self.max_voltage

    # Current flowing through the capacitor; V is Vin (charging) or Vci (discharging)
    def calculate_current(self, t, V):
        return (V / self.RESISTANCE) * math.exp(-t/self.TIME_CONSTANT)

    # Charge flowing through the capacitor, Q(t), at instant t and given Vc(t)
    def calculate_charge(self, Vc):
        return self.CAPACITANCE * Vc

    # Energy stored in capacitor, E(t), at instant t and given Vc(t)
    def calculate_energy(self, Vc):
        return (1/2) * self.CAPACITANCE * (Vc*Vc)

    # Checks if capacitor is fully charged, i.e. Vc(t) reaches the maximum possible voltage
    def is_fully_charged(self):
        return self.voltage >= self.max_voltage

    # Given an instant t and supply voltage Vin, recalculate the stats for the Energy Storage
    def refresh_energy_storage(self, t, Vin, status):
        self.status = status
        self.voltage = self.calculate_voltage(t, Vin)
        self.current = self.calculate_current(t, Vin)
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
