import unittest
from src.input.input import Input
from src.behs.energysupply import ConstantSupply, HarvestingSupply
from src.behs.energystorage import Capacitor
from src.behs.load import Resistor, MCU

_T_VECTOR = [i * 0.25 for i in range(241)]

_VALID_CONFIGS = [
    {
        "supply": {"type": "constant"},
        "storage": {"type": "capacitor"},
        "load": {"type": "resistor"},
    },
    {
        "supply": {"type": "harvesting"},
        "storage": {"type": "capacitor"},
        "load": {"type": "mcu"},
    }
]

_INVALID_CONFIGS = {
    "unknown_supply": {
        "supply": {"type": "unknown"},
    },
    "unknown_storage": {
        "supply": {"type": "constant"},
        "storage": {"type": "unknown"},
    },
    "unknown_load": {
        "supply": {"type": "constant"},
        "storage": {"type": "capacitor"},
        "load": {"type": "unknown"},
    },
    "missing_supply": {
        "storage": {"type": "capacitor"},
        "load": {"type": "resistor"},
    },
    "missing_storage": {
        "supply": {"type": "constant"},
        "load": {"type": "resistor"},
    },
    "missing_load": {
        "supply": {"type": "constant"},
        "storage": {"type": "capacitor"},
    },
}


class TestInputValidConfigs(unittest.TestCase):
    def test_init_supply_type_correctly(self):
        for config in _VALID_CONFIGS:
            sim_input = Input(config, _T_VECTOR)
            match config["supply"]["type"]:
                case "constant":
                    self.assertIsInstance(sim_input.supply, ConstantSupply)
                case "harvesting":
                    self.assertIsInstance(sim_input.supply, HarvestingSupply)

    def test_init_storage_type_correctly(self):
        for config in _VALID_CONFIGS:
            sim_input = Input(config, _T_VECTOR)
            match config["storage"]["type"]:
                case "capacitor":
                    self.assertIsInstance(sim_input.storage, Capacitor)

    def test_init_load_type_correctly(self):
        for config in _VALID_CONFIGS:
            sim_input = Input(config, _T_VECTOR)
            match config["load"]["type"]:
                case "resistor":
                    self.assertIsInstance(sim_input.load, Resistor)
                case "mcu":
                    self.assertIsInstance(sim_input.load, MCU)


class TestInputInvalidConfigs(unittest.TestCase):
    def test_invalid_supply_config(self):
        config = _INVALID_CONFIGS["unknown_supply"]
        with self.assertRaises(ValueError):
            Input(config, _T_VECTOR)

    def test_invalid_storage_config(self):
        config = _INVALID_CONFIGS["unknown_storage"]
        with self.assertRaises(ValueError):
            Input(config, _T_VECTOR)

    def test_invalid_load_config(self):
        config = _INVALID_CONFIGS["unknown_load"]
        with self.assertRaises(ValueError):
            Input(config, _T_VECTOR)

    def test_missing_supply_config(self):
        config = _INVALID_CONFIGS["missing_supply"]
        with self.assertRaises(ValueError):
            Input(config, _T_VECTOR)

    def test_missing_storage_config(self):
        config = _INVALID_CONFIGS["missing_storage"]
        with self.assertRaises(ValueError):
            Input(config, _T_VECTOR)

    def test_missing_load_config(self):
        config = _INVALID_CONFIGS["missing_load"]
        with self.assertRaises(ValueError):
            Input(config, _T_VECTOR)
