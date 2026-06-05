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

    # Run simulation and write output to local log file, 'output.log'
    out.write_to_log(t_vector, sim_input.supply,
                     sim_input.storage, sim_input.load)

    # Run simulation and write output to local CSV file, 'output.csv'
    out.write_to_csv(t_vector, sim_input.supply,
                     sim_input.storage, sim_input.load)

    # Formats CSV and writes output to local Excel file, 'output.xlsx'
    out.write_to_excel()

    # Reads Excel file and plots the output
    out.plot()
