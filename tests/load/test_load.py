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
