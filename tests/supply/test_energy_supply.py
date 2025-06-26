import unittest
from src.supply.energy_supply import ConstantSupply, HarvestingSupply
from internal.internal import Utils


class TestEnergySupply(unittest.TestCase):

    def setUp(self):
        t_vector = Utils.generate_t_vector()
        self.supply_constant = ConstantSupply(t_vector)
        self.supply_harvesting = HarvestingSupply(t_vector)

    def test_init_supply_constant(self):
        self.assertEqual(self.supply_constant.type, "constant")
        self.assertEqual(self.supply_constant.voltage, 0.0)

    def test_init_supply_harvesting(self):
        self.assertEqual(self.supply_harvesting.type, "harvesting")
        self.assertEqual(self.supply_harvesting.voltage, 0.0)


if __name__ == '__main__':
    unittest.main()
