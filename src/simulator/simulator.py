import src.output.output as out
import src.input.input as inp


def generate_t_vector(start, end, interval):
    """Generates a time vector with a given start, end and interval.
    It is used to simulate the system functions over time."""
    return [start + i *
            interval for i in range(int((end - start) / interval) + 1)]


def run():
    # Generates a time vector
    t_vector = generate_t_vector(start=0, end=60, interval=0.25)

    # Initializes the simulation input configuration
    input_config = {
        "supply": {"type": "constant"},
        "storage": {"type": "capacitor"},
        "load": {"type": "resistor"},
    }
    sim_input = inp.Input(input_config, t_vector)

    # Executes the simulation, updating the supply, storage and load at each time t
    sim_output = {}

    for i, t in enumerate(t_vector):
        sim_input.supply.refresh(t_index=i)
        sim_input.storage.refresh(t_time=t, v_supply=sim_input.supply.voltage,
                                  load_energy_consumed=sim_input.load.energy_consumed)
        sim_input.load.refresh(v_supply=sim_input.storage.voltage,
                               v_load_min=sim_input.storage.V_LOAD_MIN)

        sim_output[t] = {
            "supply": {
                "type": sim_input.supply.type,
                "voltage": sim_input.supply.voltage,
            },
            "storage": {
                "type": sim_input.storage.type,
                "voltage": sim_input.storage.voltage,
                "current": sim_input.storage.current,
                "energy_stored": sim_input.storage.energy_stored,
            },
            "load": {
                "type": sim_input.load.type,
                "voltage": sim_input.load.voltage,
                "current": sim_input.load.current,
                "energy_consumed": sim_input.load.energy_consumed,
                "total_energy_consumed": sim_input.load.total_energy_consumed,
            }
        }

    return sim_output
