import src.simulator.simulator as simulator
import src.output.output as out
import src.input.input as inp


def main():
    # # Generates a time vector with a given start, end, and interval
    t_vector = simulator.generate_t_vector(start=0, end=60, interval=0.25)

    # Initializes the simulation input configuration
    input_config = {
        "supply": {"type": "constant"},
        "storage": {"type": "capacitor"},
        "load": {"type": "resistor"},
    }
    sim_input = inp.Input(input_config, t_vector)

    # Run simulation for given input param
    sim_output = simulator.run(t_vector, sim_input)

    # Write output to local log file, 'output.log'
    out.write_to_log(sim_output)

    # Write output to local CSV file, 'output.csv'
    out.write_to_csv(sim_output)

    # Formats CSV and writes output to local Excel file, 'output.xlsx'
    out.write_to_excel()

    # Reads Excel file and plots the output
    out.plot()


if __name__ == "__main__":
    main()
