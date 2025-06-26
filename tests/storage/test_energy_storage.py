import unittest
from src.storage.energy_storage import Capacitor


class TestEnergyStorage(unittest.TestCase):

    def setUp(self):
        self.storage_capacitor = Capacitor()

    def test_init(self):
        self.assertEqual(self.storage_capacitor.type, "capacitor")
        self.assertEqual(self.storage_capacitor.voltage, 0.0)
        self.assertEqual(self.storage_capacitor.current, 0.0)
        self.assertEqual(self.storage_capacitor.energy, 0.0)


if __name__ == '__main__':
    unittest.main()
