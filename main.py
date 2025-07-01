import pandas as pd
import output
from src.storage.energy_storage import Capacitor
from src.supply.energy_supply import ConstantSupply
from src.load.load import Resistor


# Generates a time vector with a given start, end and interval
# It is used to simulate the energy supply, storage, and load over time
def generate_t_vector(start, end, interval):
    return [start + i *
            interval for i in range(int((end - start) / interval) + 1)]


# Main function to run the simulation
def main():
    # Generates a time vector
    t_vector = generate_t_vector(start=0, end=60, interval=0.25)

    # Initializes the components of the simulation
    supply = ConstantSupply(t_vector)
    storage = Capacitor()
    load = Resistor()

    # Writes output of simulation to local log file, 'output.log'
    output.write_to_log(t_vector, supply, storage, load)

    # Formats and writes output to local CSV file, 'output.csv'
    output.write_to_csv(t_vector, supply, storage, load)

    # Formats and writes output to local Excel file, 'output.xlsx'
    output.write_to_excel()

    # Reads Excel file and plots the output
    output.plot()


if __name__ == "__main__":
    main()
