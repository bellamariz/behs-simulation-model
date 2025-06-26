import unittest
from src.supply.energy_supply import ConstantSupply, HarvestingSupply


class TestEnergySupply(unittest.TestCase):

    def generate_t_vector(self):
        start = 0.0
        end = 6.0
        interval = 0.25
        return [start + i *
                interval for i in range(int((end - start) / interval) + 1)]

    def setUp(self):
        t_vector = self.generate_t_vector()
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
