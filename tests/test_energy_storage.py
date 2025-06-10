import unittest
from src.energy_storage import EnergyStorage

class TestEnergyStorage(unittest.TestCase):

	def setUp(self):
		self.storage = EnergyStorage(capacity=100)

	def test_charge(self):
		self.storage.charge(50)
		self.assertEqual(self.storage.current_charge, 50)

		self.storage.charge(60)  # Exceeding capacity
		self.assertEqual(self.storage.current_charge, 100)

	def test_discharge(self):
		self.storage.charge(80)
		retrieved = self.storage.discharge(30)
		self.assertEqual(retrieved, 30)
		self.assertEqual(self.storage.current_charge, 50)

		retrieved = self.storage.discharge(100)  # Trying to retrieve more than available
		self.assertEqual(retrieved, 50)
		self.assertEqual(self.storage.current_charge, 0)

	def test_get_energy_level(self):
		self.storage.charge(40)
		self.assertEqual(self.storage.get_energy_level(), 40)

		self.storage.discharge(20)
		self.assertEqual(self.storage.get_energy_level(), 20)

if __name__ == '__main__':
	unittest.main()