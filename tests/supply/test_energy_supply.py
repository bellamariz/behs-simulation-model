import unittest
from unittest.mock import patch
from src.supply.energy_supply import ConstantSupply, HarvestingSupply


class TestEnergySupply(unittest.TestCase):
    def setUp(self):
        self.t_vector = [0, 0.25, 0.5, 0.75, 1.0]
        self.supply_constant = ConstantSupply(self.t_vector)
        # Mock random.uniform to return fixed values for testing
        with patch('random.uniform') as mock_random:
            mock_random.side_effect = [1.0, 3.5, 7.2, 9.8, 5.4]
            self.supply_harvesting = HarvestingSupply(self.t_vector)

    def test_init_supply_constant(self):
        self.assertEqual(self.supply_constant.type, "constant")
        self.assertEqual(self.supply_constant.voltage, 0.0)
        self.assertEqual(len(self.supply_constant.profile), len(self.t_vector))
        for voltage in self.supply_constant.profile:
            self.assertEqual(voltage, 8.0)

    def test_init_supply_harvesting(self):
        self.assertEqual(self.supply_harvesting.type, "harvesting")
        self.assertEqual(self.supply_harvesting.voltage, 0.0)
        self.assertEqual(len(self.supply_harvesting.profile),
                         len(self.t_vector))


class TestConstantSupply(unittest.TestCase):
    def setUp(self):
        self.t_vector = [0, 0.25, 0.5, 0.75, 1.0]
        self.supply_constant = ConstantSupply(self.t_vector)

    def test_init_empty_vector(self):
        empty_vector = []
        supply = ConstantSupply(empty_vector)

        self.assertEqual(len(supply.profile), 0)
        self.assertEqual(supply.type, "constant")

    def test_init_single_element_vector(self):
        single_vector = [0]
        supply = ConstantSupply(single_vector)

        self.assertEqual(len(supply.profile), 1)
        self.assertEqual(supply.profile[0], 8.0)

    def test_refresh_different_time_indexes(self):
        t_index = 2
        self.supply_constant.refresh(t_index)
        self.assertEqual(self.supply_constant.voltage, 8.0)

        t_index = 0
        self.supply_constant.refresh(t_index)
        self.assertEqual(self.supply_constant.voltage, 8.0)

        t_index = len(self.t_vector) - 1
        self.supply_constant.refresh(t_index)
        self.assertEqual(self.supply_constant.voltage, 8.0)

        t_index = -1
        self.supply_constant.refresh(t_index)
        self.assertEqual(self.supply_constant.voltage, 8.0)

        t_index = len(self.t_vector)
        with self.assertRaises(IndexError):
            self.supply_constant.refresh(t_index)

    def test_profile_immutable_after_init(self):
        original_profile = self.supply_constant.profile.copy()

        self.supply_constant.refresh(0)
        self.supply_constant.refresh(2)

        self.assertEqual(self.supply_constant.profile, original_profile)


class TestHarvestingSupply(unittest.TestCase):
    def setUp(self):
        self.t_vector = [0, 0.25, 0.5, 0.75, 1.0]
        # Mock random.uniform to return fixed values for testing
        with patch('random.uniform') as mock_random:
            mock_random.side_effect = [1.0, 3.5, 7.2, 9.8, 5.4]
            self.supply_harvesting = HarvestingSupply(self.t_vector)

    def test_init_profile_values_in_range(self):
        supply = HarvestingSupply([0, 1, 2])

        for voltage in supply.profile:
            self.assertGreaterEqual(voltage, 0.0)
            self.assertLessEqual(voltage, supply.MAX_SUPPLY_VOLTAGE)

    def test_init_empty_vector(self):
        empty_vector = []
        supply = HarvestingSupply(empty_vector)

        self.assertEqual(len(supply.profile), 0)
        self.assertEqual(supply.type, "harvesting")

    def test_init_single_element_vector(self):
        single_vector = [0]
        supply = HarvestingSupply(single_vector)

        self.assertEqual(len(supply.profile), 1)
        self.assertGreaterEqual(supply.profile[0], 0.0)
        self.assertLessEqual(supply.profile[0], supply.MAX_SUPPLY_VOLTAGE)

    def test_refresh_different_time_indexes(self):
        t_index = 2
        expected_voltage = self.supply_harvesting.profile[t_index]
        self.supply_harvesting.refresh(t_index)
        self.assertEqual(self.supply_harvesting.voltage, expected_voltage)

        t_index = 0
        expected_voltage = self.supply_harvesting.profile[t_index]
        self.supply_harvesting.refresh(t_index)
        self.assertEqual(self.supply_harvesting.voltage, expected_voltage)

        t_index = len(self.t_vector) - 1
        expected_voltage = self.supply_harvesting.profile[t_index]
        self.supply_harvesting.refresh(t_index)
        self.assertEqual(self.supply_harvesting.voltage, expected_voltage)

        t_index = -1
        expected_voltage = self.supply_harvesting.profile[t_index]
        self.supply_harvesting.refresh(t_index)
        self.assertEqual(self.supply_harvesting.voltage, expected_voltage)

        t_index = len(self.t_vector)  # Out of bounds
        with self.assertRaises(IndexError):
            self.supply_harvesting.refresh(t_index)

    def test_profile_immutable_after_init(self):
        original_profile = self.supply_harvesting.profile.copy()

        self.supply_harvesting.refresh(0)
        self.supply_harvesting.refresh(2)

        self.assertEqual(self.supply_harvesting.profile, original_profile)


if __name__ == '__main__':
    unittest.main()
