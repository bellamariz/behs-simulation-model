import unittest
from src.load.load import Resistor, MCU


class TestLoad(unittest.TestCase):
    def setUp(self):
        self.load_resistor = Resistor()
        self.load_mcu = MCU()

    def test_init_load_resistor(self):
        self.assertEqual(self.load_resistor.type, "resistor")
        self.assertEqual(self.load_resistor.operating_voltage,
                         Resistor.OPERATING_VOLTAGE)
        self.assertEqual(self.load_resistor.voltage, 0.0)
        self.assertEqual(self.load_resistor.current, 0.0)
        self.assertEqual(self.load_resistor.energy_consumed, 0.0)

    def test_init_load_mcu(self):
        self.assertEqual(self.load_mcu.type, "mcu")
        self.assertEqual(self.load_mcu.operating_voltage,
                         MCU.OPERATING_VOLTAGE)
        self.assertEqual(self.load_mcu.voltage, 0.0)
        self.assertEqual(self.load_mcu.current, 0.0)
        self.assertEqual(self.load_mcu.energy_consumed, 0.0)


class TestLoadResistor(unittest.TestCase):
    def setUp(self):
        self.load_resistor = Resistor()

    def test_calculate_current_insufficient_storage_supply(self):
        # Default Resistor operating voltage is 1.0V
        # Supply voltage from storage is 0.5V (below operating voltage)
        actual_current = self.load_resistor.calculate_current(
            v_supply=0.5, v_load_min=1.0)

        self.assertEqual(actual_current, 0.0)

    def test_calculate_current_sufficient_storage_supply(self):
        # Default Resistor operating voltage is 1.0V
        # Supply voltage from storage is 2.0V (above operating voltage)
        actual_current = self.load_resistor.calculate_current(
            v_supply=2.0, v_load_min=1.0)
        expected_current = 2.0 / Resistor.RESISTANCE

        self.assertEqual(actual_current, expected_current)

    def test_calculate_current_sufficient_storage_supply_but_below_load_min(self):
        # Default Resistor operating voltage is 1.0V
        # Supply voltage from storage is 1.5V, but v_load_min is 2.0V
        actual_current = self.load_resistor.calculate_current(
            v_supply=1.5, v_load_min=2.0)

        self.assertEqual(actual_current, 0.0)

    def test_calculate_voltage_insufficient_storage_supply(self):
        actual_voltage = self.load_resistor.calculate_voltage(
            v_supply=0.5, v_load_min=1.0)

        self.assertEqual(actual_voltage, 0.0)

    def test_calculate_voltage_sufficient_storage_supply(self):
        actual_voltage = self.load_resistor.calculate_voltage(
            v_supply=2.0, v_load_min=1.0)
        expected_voltage = 2.0  # same as v_supply

        self.assertEqual(actual_voltage, expected_voltage)

    def test_calculate_energy_consumed_insufficient_storage_supply(self):
        actual_energy_consumed = self.load_resistor.calculate_energy_consumed(
            v_supply=0.5, v_load_min=1.0)

        self.assertEqual(actual_energy_consumed, 0.0)

    def test_calculate_energy_consumed_sufficient_storage_supply(self):
        actual_energy_consumed = self.load_resistor.calculate_energy_consumed(
            v_supply=2.0, v_load_min=1.0)
        expected_energy_consumed = Resistor.ENERGY_CONSUMPTION

        self.assertEqual(actual_energy_consumed, expected_energy_consumed)

    def test_refresh_single_time(self):
        self.load_resistor.refresh(v_supply=2.0, v_load_min=1.0)

        self.assertEqual(self.load_resistor.voltage, 2.0)
        self.assertEqual(self.load_resistor.current, 0.002)
        self.assertEqual(self.load_resistor.energy_consumed, 0.001)
        self.assertEqual(self.load_resistor.total_energy_consumed, 0.001)

    def test_refresh_multiple_times_with_constant_supply(self):
        self.load_resistor.refresh(v_supply=2.0, v_load_min=1.0)
        self.load_resistor.refresh(v_supply=2.0, v_load_min=1.0)

        self.assertEqual(self.load_resistor.total_energy_consumed, 0.002)


class TestLoadMCU(unittest.TestCase):
    def setUp(self):
        self.load_mcu = MCU()

    def test_calculate_current_insufficient_storage_supply(self):
        # Default MCU operating voltage is 3.3V
        # Supply voltage from storage is 2.0V (below operating voltage)
        actual_current = self.load_mcu.calculate_current(
            v_supply=2.0, v_load_min=3.3)

        self.assertEqual(actual_current, 0.0)

    def test_calculate_current_sufficient_storage_supply(self):
        # Default MCU operating voltage is 3.3V
        # Supply voltage from storage is 5.0V (above operating voltage)
        actual_current = self.load_mcu.calculate_current(
            v_supply=5.0, v_load_min=3.3)
        expected_current = MCU.OPERATING_CURRENT

        self.assertEqual(actual_current, expected_current)

    def test_calculate_current_sufficient_storage_supply_but_below_load_min(self):
        # Default MCU operating voltage is 3.3V
        # Supply voltage from storage is 3.5V, but v_load_min is 4.0V
        actual_current = self.load_mcu.calculate_current(
            v_supply=3.5, v_load_min=4.0)

        self.assertEqual(actual_current, 0.0)

    def test_calculate_voltage_insufficient_storage_supply(self):
        actual_voltage = self.load_mcu.calculate_voltage(
            v_supply=2.0, v_load_min=3.3)

        self.assertEqual(actual_voltage, 0.0)

    def test_calculate_voltage_sufficient_storage_supply(self):
        actual_voltage = self.load_mcu.calculate_voltage(
            v_supply=5.0, v_load_min=3.3)
        expected_voltage = MCU.OPERATING_VOLTAGE

        self.assertEqual(actual_voltage, expected_voltage)

    def test_calculate_energy_consumed_insufficient_storage_supply(self):
        actual_energy_consumed = self.load_mcu.calculate_energy_consumed(
            v_supply=2.0, v_load_min=3.3)

        self.assertEqual(actual_energy_consumed, 0.0)

    def test_calculate_energy_consumed_sufficient_storage_supply(self):
        actual_energy_consumed = self.load_mcu.calculate_energy_consumed(
            v_supply=5.0, v_load_min=3.3)
        expected_energy_consumed = MCU.ENERGY_CONSUMPTION

        self.assertEqual(actual_energy_consumed, expected_energy_consumed)

    def test_refresh_single_time(self):
        self.load_mcu.refresh(v_supply=5.0, v_load_min=3.3)

        self.assertEqual(self.load_mcu.voltage, MCU.OPERATING_VOLTAGE)
        self.assertEqual(self.load_mcu.current, MCU.OPERATING_CURRENT)
        self.assertEqual(self.load_mcu.energy_consumed, MCU.ENERGY_CONSUMPTION)
        self.assertEqual(self.load_mcu.total_energy_consumed,
                         MCU.ENERGY_CONSUMPTION)

    def test_refresh_multiple_times_with_constant_supply(self):
        self.load_mcu.refresh(v_supply=5.0, v_load_min=3.3)
        self.load_mcu.refresh(v_supply=5.0, v_load_min=3.3)

        self.assertEqual(self.load_mcu.total_energy_consumed,
                         MCU.ENERGY_CONSUMPTION * 2)


if __name__ == '__main__':
    unittest.main()
