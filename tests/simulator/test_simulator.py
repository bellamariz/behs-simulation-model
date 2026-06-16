import src.simulator.simulator as simulator
import src.input.input as inp
import unittest


class TestGenerateTVector(unittest.TestCase):
    def test_vector_with_integer_interval(self):
        t_vector = simulator.generate_t_vector(start=0, end=5, interval=1)
        self.assertEqual(t_vector, [0, 1, 2, 3, 4, 5])

    def test_vector_with_float_interval(self):
        t_vector = simulator.generate_t_vector(start=0, end=1, interval=0.25)
        self.assertEqual(t_vector, [0, 0.25, 0.5, 0.75, 1.0])


class TestSimulatorRun(unittest.TestCase):
    def setUp(self):
        self.t_vector = simulator.generate_t_vector(
            start=0, end=10, interval=0.25)
        input_config = {
            "supply": {"type": "constant"},
            "storage": {"type": "capacitor"},
            "load": {"type": "resistor"},
        }
        self.sim_input = inp.Input(input_config, self.t_vector)

    def test_run_with_empty_input(self):
        with self.assertRaises(ValueError):
            simulator.run(self.t_vector, inp.Input({}, self.t_vector))

    def test_run_with_valid_input(self):
        try:
            output = simulator.run(self.t_vector, self.sim_input)
            self.assertIsNotNone(output)
        except Exception as e:
            self.fail(
                f"simulator.run() raised {type(e).__name__} unexpectedly: {e}")

    def test_run_validate_output_structure(self):
        output = simulator.run(self.t_vector, self.sim_input)
        required_keys = {"supply", "storage", "load"}

        self.assertGreater(len(output), 0)
        for time_point in output.values():
            self.assertIsInstance(time_point, dict)
            self.assertEqual(set(time_point.keys()), required_keys)

    def test_run_validate_output_data(self):
        output = simulator.run(self.t_vector, self.sim_input)
        supply_keys = {"type", "voltage"}
        storage_keys = {"type", "status",
                        "voltage", "current", "energy_stored"}
        load_keys = {"type", "voltage", "current",
                     "energy_consumed", "total_energy_consumed"}

        for data in output.values():
            self.assertEqual(set(data["supply"].keys()), supply_keys)
            self.assertIsInstance(data["supply"]["type"], str)
            self.assertIsInstance(
                data["supply"]["voltage"], (float))

            self.assertEqual(set(data["storage"].keys()), storage_keys)
            self.assertIsInstance(data["storage"]["type"], str)
            self.assertIsInstance(data["storage"]["status"], str)
            self.assertIsInstance(
                data["storage"]["voltage"], (float))
            self.assertIsInstance(
                data["storage"]["current"], (float))
            self.assertIsInstance(
                data["storage"]["energy_stored"], (float))

            self.assertEqual(set(data["load"].keys()), load_keys)
            self.assertIsInstance(data["load"]["type"], str)
            self.assertIsInstance(data["load"]["voltage"], (float))
            self.assertIsInstance(data["load"]["current"], (float))
            self.assertIsInstance(
                data["load"]["energy_consumed"], (float))
            self.assertIsInstance(
                data["load"]["total_energy_consumed"], (float)
            )


if __name__ == "__main__":
    unittest.main()
