import unittest
import math
from src.behs.energystorage import Capacitor


class TestEnergyStorage(unittest.TestCase):
    def setUp(self):
        self.storage_capacitor = Capacitor()

    def test_init(self):
        self.assertEqual(self.storage_capacitor.type, "capacitor")
        self.assertEqual(self.storage_capacitor.voltage, 0.0)
        self.assertEqual(self.storage_capacitor.current, 0.0)
        self.assertEqual(self.storage_capacitor.energy, 0.0)


class TestCapacitor(unittest.TestCase):
    def setUp(self):
        self.storage_capacitor = Capacitor()

    def test_charging_voltage(self):
        t_time = 1.0
        v_supply = 10.0

        expected_voltage = v_supply * \
            (1 - math.exp(-t_time / Capacitor.TIME_CONSTANT))
        actual_voltage = self.storage_capacitor.charging_voltage(
            t_time, v_supply)

        self.assertAlmostEqual(actual_voltage, expected_voltage, places=5)

    def test_charging_voltage_zero_time(self):
        # When t = 0, voltage --> 0
        actual_voltage = self.storage_capacitor.charging_voltage(
            t_time=0.0, v_supply=10.0)

        self.assertEqual(actual_voltage, 0.0)

    def test_charging_voltage_long_time(self):
        # When t --> infinity, voltage --> V_MAX
        actual_voltage = self.storage_capacitor.charging_voltage(
            t_time=1000.0, v_supply=10.0)

        self.assertAlmostEqual(actual_voltage, 10.0, places=3)

    def test_discharging_voltage(self):
        self.storage_capacitor.v_discharge_init = 5.0
        t_time = 1.0

        expected_voltage = self.storage_capacitor.v_discharge_init * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        actual_voltage = self.storage_capacitor.discharging_voltage(t_time)

        self.assertAlmostEqual(actual_voltage, expected_voltage, places=5)

    def test_discharging_voltage_zero_time(self):
        # When t = 0, voltage --> V_MAX
        self.storage_capacitor.v_discharge_init = 5.0

        actual_voltage = self.storage_capacitor.discharging_voltage(t_time=0.0)

        self.assertEqual(actual_voltage, 5.0)

    def test_discharging_voltage_long_time(self):
        # When t --> infinity, voltage --> 0
        self.storage_capacitor.v_discharge_init = 5.0

        actual_voltage = self.storage_capacitor.discharging_voltage(
            t_time=1000.0)

        # Using assertAlmostEqual to compare floats without precision issues
        self.assertAlmostEqual(actual_voltage, 0.0, places=3)

    def test_calculate_voltage_status_charging(self):
        self.storage_capacitor.status = "charging"
        self.storage_capacitor.t_ref = 0.0
        self.storage_capacitor.v_charge_init = 2.0
        self.storage_capacitor.voltage = 2.0

        expected_voltage = self.storage_capacitor.charging_voltage(
            t_time=1.0, v_supply=10.0)
        actual_voltage = self.storage_capacitor.calculate_voltage(
            t_time=1.0, v_supply=10.0)

        self.assertAlmostEqual(actual_voltage, expected_voltage, places=5)

    def test_calculate_voltage_status_discharging(self):
        self.storage_capacitor.status = "discharging"
        self.storage_capacitor.t_ref = 0.0
        self.storage_capacitor.v_discharge_init = 4.0
        self.storage_capacitor.voltage = 4.0

        expected_voltage = self.storage_capacitor.discharging_voltage(
            t_time=1.0)
        actual_voltage = self.storage_capacitor.calculate_voltage(
            t_time=1.0, v_supply=10.0)

        self.assertAlmostEqual(actual_voltage, expected_voltage, places=5)

    def test_calculate_voltage_charging_to_ready(self):
        # When voltage charges to V_MAX, status changes to "ready"
        self.storage_capacitor.status = "charging"
        self.storage_capacitor.t_ref = 0.0
        self.storage_capacitor.v_charge_init = Capacitor.V_MAX
        self.storage_capacitor.voltage = Capacitor.V_MAX

        actual_voltage = self.storage_capacitor.calculate_voltage(
            t_time=1.0, v_supply=10.0)

        self.assertEqual(actual_voltage, Capacitor.V_MAX)
        self.assertEqual(self.storage_capacitor.status, "ready")

    def test_calculate_voltage_discharging_to_idle(self):
        # When voltage drops to V_LOAD_MIN, status transitions to "idle"
        self.storage_capacitor.status = "discharging"
        self.storage_capacitor.t_ref = 0.0
        self.storage_capacitor.v_discharge_init = Capacitor.V_LOAD_MIN
        self.storage_capacitor.voltage = Capacitor.V_LOAD_MIN

        actual_voltage = self.storage_capacitor.calculate_voltage(
            t_time=1.0, v_supply=10.0)

        self.assertLessEqual(actual_voltage, Capacitor.V_LOAD_MIN)
        self.assertEqual(self.storage_capacitor.status, "idle")

    def test_calculate_current_charging(self):
        self.storage_capacitor.status = "charging"
        self.storage_capacitor.t_ref = 0.0
        self.storage_capacitor.v_charge_init = 2.0
        self.storage_capacitor.voltage = 2.0

        t_time = 1.0
        v_supply = 10.0

        expected_current = ((v_supply - 2.0) / Capacitor.R_SERIES) * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        actual_current = self.storage_capacitor.calculate_current(
            t_time, v_supply)
        self.assertAlmostEqual(actual_current, expected_current, places=5)

    def test_calculate_current_discharging(self):
        self.storage_capacitor.status = "discharging"
        self.storage_capacitor.t_ref = 0.0
        self.storage_capacitor.v_discharge_init = 6.0
        self.storage_capacitor.voltage = 6.0

        t_time = 1.0
        v_supply = 10.0

        expected_current = (6.0 / Capacitor.R_SERIES) * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        actual_current = self.storage_capacitor.calculate_current(
            t_time, v_supply)

        self.assertAlmostEqual(actual_current, expected_current, places=5)

    def test_calculate_current_zero_elapsed_time(self):
        self.storage_capacitor.status = "charging"
        self.storage_capacitor.t_ref = 0.0
        self.storage_capacitor.v_charge_init = 0.0
        self.storage_capacitor.voltage = 0.0

        expected_current = 10.0 / Capacitor.R_SERIES
        actual_current = self.storage_capacitor.calculate_current(
            t_time=0.0, v_supply=10.0)

        self.assertAlmostEqual(actual_current, expected_current, places=5)

    def test_calculate_energy_stored_charging(self):
        # Assuming capacitor is in "charging" status
        # Initial voltage below V_LOAD_MIN
        self.storage_capacitor.voltage = 3.0
        load_energy_consumed = 0.01

        expected_energy = (1/2) * Capacitor.CAPACITANCE * \
            (self.storage_capacitor.voltage ** 2)
        actual_energy = self.storage_capacitor.calculate_energy_stored(
            load_energy_consumed)

        self.assertAlmostEqual(actual_energy, expected_energy, places=5)

    def test_calculate_energy_stored_discharging(self):
        # Assume capacitor is in "discharging" status
        # Initial voltage above V_LOAD_MIN
        self.storage_capacitor.status = "discharging"
        self.storage_capacitor.voltage = 6.0
        load_energy_consumed = 0.02
        capacitor_energy = (1/2) * Capacitor.CAPACITANCE * \
            (self.storage_capacitor.voltage ** 2)

        expected_energy = capacitor_energy - load_energy_consumed
        actual_energy = self.storage_capacitor.calculate_energy_stored(
            load_energy_consumed)

        self.assertAlmostEqual(actual_energy, expected_energy, places=5)

    def test_calculate_energy_stored_zero_voltage(self):
        self.storage_capacitor.voltage = 0.0
        load_energy_consumed = 0.01

        actual_energy = self.storage_capacitor.calculate_energy_stored(
            load_energy_consumed)

        self.assertEqual(actual_energy, 0.0)

    def test_refresh(self):
        self.storage_capacitor.status = "charging"
        self.storage_capacitor.t_ref = 0.0
        self.storage_capacitor.v_charge_init = 2.0
        self.storage_capacitor.voltage = 2.0

        t_time = 1.0
        v_supply = 10.0
        load_energy_consumed = 0.01

        self.storage_capacitor.refresh(t_time, v_supply, load_energy_consumed)

        expected_voltage = v_supply + (2.0 - v_supply) * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        expected_current = ((v_supply - 2.0) / Capacitor.R_SERIES) * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        expected_energy = (1/2) * Capacitor.CAPACITANCE * \
            (self.storage_capacitor.voltage ** 2)

        self.assertAlmostEqual(
            self.storage_capacitor.voltage, expected_voltage, places=5)
        self.assertAlmostEqual(
            self.storage_capacitor.current, expected_current, places=5)
        self.assertAlmostEqual(
            self.storage_capacitor.energy_stored, expected_energy, places=5)


if __name__ == '__main__':
    unittest.main()
