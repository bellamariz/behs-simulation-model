import unittest
import math
from unittest.mock import patch
from src.storage.energy_storage import Capacitor


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

        # Using assertAlmostEqual to compare floats without precision issues
        self.assertAlmostEqual(actual_voltage, expected_voltage, places=5)

    def test_charging_voltage_zero_time(self):
        actual_voltage = self.storage_capacitor.charging_voltage(
            t_time=0.0, v_supply=10.0)

        self.assertEqual(actual_voltage, 0.0)

    def test_charging_voltage_long_time(self):
        # After a long time, capacitor voltage should approach v_supply
        actual_voltage = self.storage_capacitor.charging_voltage(
            t_time=1000.0, v_supply=10.0)

        # Using assertAlmostEqual to compare floats without precision issues
        self.assertAlmostEqual(actual_voltage, 10.0, places=3)

    def test_discharging_voltage(self):
        self.storage_capacitor.voltage = 5.0
        t_time = 1.0

        expected_voltage = self.storage_capacitor.voltage * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        actual_voltage = self.storage_capacitor.discharging_voltage(t_time)

        # Using assertAlmostEqual to compare floats without precision issues
        self.assertAlmostEqual(actual_voltage, expected_voltage, places=5)

    def test_discharging_voltage_zero_time(self):
        self.storage_capacitor.voltage = 5.0

        actual_voltage = self.storage_capacitor.discharging_voltage(t_time=0.0)

        self.assertEqual(actual_voltage, 5.0)

    def test_discharging_voltage_long_time(self):
        # After a long time, capacitor voltage should approach 0V
        self.storage_capacitor.voltage = 5.0

        actual_voltage = self.storage_capacitor.discharging_voltage(
            t_time=1000.0)

        # Using assertAlmostEqual to compare floats without precision issues
        self.assertAlmostEqual(actual_voltage, 0.0, places=3)

    def test_calculate_voltage_charging_below_load_min(self):
        # Capacitor voltage below V_LOAD_MIN
        self.storage_capacitor.voltage = 2.0

        expected_voltage = self.storage_capacitor.charging_voltage(
            t_time=1.0, v_supply=10.0)
        actual_voltage = self.storage_capacitor.calculate_voltage(
            t_time=1.0, v_supply=10.0)

        # Using assertAlmostEqual to compare floats without precision issues
        self.assertAlmostEqual(actual_voltage, expected_voltage, places=5)

    def test_calculate_voltage_discharging_above_load_min(self):
        # Capacitor voltage above V_LOAD_MIN
        self.storage_capacitor.voltage = 6.0

        expected_voltage = self.storage_capacitor.voltage - \
            self.storage_capacitor.discharging_voltage(t_time=1.0)
        actual_voltage = self.storage_capacitor.calculate_voltage(
            t_time=1.0, v_supply=10.0)

        # Using assertAlmostEqual to compare floats without precision issues
        self.assertAlmostEqual(actual_voltage, expected_voltage, places=5)

    @patch('builtins.print')
    def test_calculate_voltage_at_max_capacity(self, mock_print):
        self.storage_capacitor.voltage = 12.0

        expected_voltage = self.storage_capacitor.calculate_voltage(
            t_time=1.0, v_supply=10.0)

        self.assertEqual(expected_voltage, Capacitor.V_STORAGE_MAX)
        mock_print.assert_called_once_with(
            f"Energy storage is at maximum capacity {Capacitor.V_STORAGE_MAX}V")

    def test_calculate_current_charging_below_load_min(self):
        # Capacitor voltage below V_LOAD_MIN
        self.storage_capacitor.voltage = 2.0

        t_time = 1.0
        v_supply = 10.0

        expected_current = (v_supply / Capacitor.RESISTANCE) * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        actual_current = self.storage_capacitor.calculate_current(
            t_time, v_supply)
        self.assertAlmostEqual(actual_current, expected_current, places=5)

    def test_calculate_current_discharging_above_load_min(self):
        # Capacitor voltage above V_LOAD_MIN
        self.storage_capacitor.voltage = 6.0

        t_time = 1.0
        v_supply = 10.0

        expected_current = (self.storage_capacitor.voltage / Capacitor.RESISTANCE) * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        actual_current = self.storage_capacitor.calculate_current(
            t_time, v_supply)

        self.assertAlmostEqual(actual_current, expected_current, places=5)

    def test_calculate_current_zero_time(self):
        self.storage_capacitor.voltage = 2.0

        expected_current = 10.0 / Capacitor.RESISTANCE
        actual_current = self.storage_capacitor.calculate_current(
            t_time=0.0, v_supply=10.0)

        self.assertAlmostEqual(actual_current, expected_current, places=5)

    def test_calculate_energy_stored_charging(self):
        # Assume capacitor is in charging scenario
        # Set initial voltage below V_LOAD_MIN
        self.storage_capacitor.voltage = 3.0
        load_energy_consumed = 0.01

        expected_energy = (1/2) * Capacitor.CAPACITANCE * \
            (self.storage_capacitor.voltage ** 2)
        actual_energy = self.storage_capacitor.calculate_energy_stored(
            load_energy_consumed)

        self.assertAlmostEqual(actual_energy, expected_energy, places=5)

    def test_calculate_energy_stored_discharging(self):
        # Assume capacitor is in discharging scenario
        # Set initial voltage above V_LOAD_MIN
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
        # Assume capacitor is in charging scenario
        # Set initial voltage below V_LOAD_MIN
        self.storage_capacitor.voltage = 2.0
        t_time = 1.0
        v_supply = 10.0
        load_energy_consumed = 0.01

        self.storage_capacitor.refresh(t_time, v_supply, load_energy_consumed)

        expected_voltage = self.storage_capacitor.charging_voltage(
            t_time, v_supply)
        expected_current = (v_supply / Capacitor.RESISTANCE) * \
            math.exp(-t_time / Capacitor.TIME_CONSTANT)
        expected_energy = (1/2) * Capacitor.CAPACITANCE * \
            (self.storage_capacitor.voltage ** 2)

        # Using assertAlmostEqual to compare floats without precision issues
        self.assertAlmostEqual(
            self.storage_capacitor.voltage, expected_voltage, places=5)
        self.assertAlmostEqual(
            self.storage_capacitor.current, expected_current, places=5)
        self.assertAlmostEqual(
            self.storage_capacitor.energy_stored, expected_energy, places=5)


if __name__ == '__main__':
    unittest.main()
