import src.simulator.simulator as simulator
import src.output.output as out


def main():
    # Run simulation
    sim_output = simulator.run()

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
