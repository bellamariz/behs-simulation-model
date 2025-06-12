import unittest
from src.energy_storage import EnergyStorage


class TestEnergyStorage(unittest.TestCase):

    def setUp(self):
        self.storage = EnergyStorage(vmax=300, vin=10)

    def test_init(self):
        self.assertEqual(self.storage.status, "empty")
        self.assertEqual(self.storage.max_voltage, 300)
        self.assertEqual(self.storage.voltage, 0)
        self.assertEqual(self.storage.current, 0.004)
        self.assertEqual(self.storage.charge, 0)
        self.assertEqual(self.storage.energy, 0)


if __name__ == '__main__':
    unittest.main()
