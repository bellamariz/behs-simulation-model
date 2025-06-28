import pandas as pd
import output
from src.storage.energy_storage import Capacitor
from src.supply.energy_supply import ConstantSupply
from src.load.load import Resistor


def generate_t_vector():
    start = 0.0
    end = 60.0
    interval = 0.25
    return [start + i *
            interval for i in range(int((end - start) / interval) + 1)]


def main():
    t_vector = generate_t_vector()
    supply = ConstantSupply(t_vector)
    storage = Capacitor()
    load = Resistor()

    # uncomment the following line to write output to a log file
    # output.write_output_to_log(t_vector, supply, storage, load)

    # write output to CSV
    output.write_output_to_csv(t_vector, supply, storage, load)

    # write output to Excel file
    df = pd.read_csv("output.csv")
    df.to_excel("output.xlsx", index=False, na_rep="NaN")

    output.plot_output()


if __name__ == "__main__":
    main()
