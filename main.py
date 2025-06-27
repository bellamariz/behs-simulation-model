import csv
import pandas as pd
from src.storage.energy_storage import Capacitor
from src.supply.energy_supply import ConstantSupply
from src.load.load import Resistor


def generate_t_vector():
    start = 0.0
    end = 60.0
    interval = 0.25
    return [start + i *
            interval for i in range(int((end - start) / interval) + 1)]


def write_output_to_log(t_vector, supply, storage, load):
    with open("output.log", "w", encoding="utf-8") as logfile:
        print("Simulation started", file=logfile)
        for i, t in enumerate(t_vector):
            print(f"Time step {i}: t={t:.2f}s\n", file=logfile)

            supply.refresh(t_index=i)
            supply.print(t_index=i, file=logfile)

            storage.refresh(t_time=t, v_supply=supply.voltage,
                            load_energy_consumed=load.energy_consumed)
            storage.print(t_index=i, file=logfile)

            load.refresh(v_supply=storage.voltage,
                         v_load_min=storage.V_LOAD_MIN)
            load.print(t_index=i, file=logfile)

            print("-" * 50, file=logfile)


def write_output_to_csv(t_vector, supply, storage, load):
    with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["step", "time", "component", "voltage", "current",
                      "energy_stored", "energy_consumed", "total_energy_consumed"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, t in enumerate(t_vector):
            supply.refresh(t_index=i)
            storage.refresh(t_time=t, v_supply=supply.voltage,
                            load_energy_consumed=load.energy_consumed)
            load.refresh(v_supply=storage.voltage,
                         v_load_min=storage.V_LOAD_MIN)

            writer.writerow({
                "step": i,
                "time": t,
                "component": "supply",
                "voltage": supply.voltage,
                "current": "NaN",
                "energy_stored": "NaN",
                "energy_consumed": "NaN",
                "total_energy_consumed": "NaN",
            })
            writer.writerow({
                "step": i,
                "time": t,
                "component": "storage",
                "voltage": storage.voltage,
                "current": storage.current,
                "energy_stored": storage.energy_stored,
                "energy_consumed": "NaN",
                "total_energy_consumed": "NaN",
            })
            writer.writerow({
                "step": i,
                "time": t,
                "component": "load",
                "voltage": load.voltage,
                "current": load.current,
                "energy_stored": "NaN",
                "energy_consumed": load.energy_consumed,
                "total_energy_consumed": load.total_energy_consumed
            })


def main():
    t_vector = generate_t_vector()
    supply = ConstantSupply(t_vector)
    storage = Capacitor()
    load = Resistor()

    # Uncomment the following line to write output to a log file
    # write_output_to_log(t_vector, supply, storage, load)

    # Write output to CSV
    write_output_to_csv(t_vector, supply, storage, load)

    # Read the CSV file
    df = pd.read_csv("output.csv")

    # Write to Excel file
    df.to_excel("output.xlsx", index=False, na_rep='NaN')


if __name__ == "__main__":
    main()
