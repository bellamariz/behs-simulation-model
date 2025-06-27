import csv
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
    with open("output.log", "w") as logfile:
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


def main():
    t_vector = generate_t_vector()
    supply = ConstantSupply(t_vector)
    storage = Capacitor()
    load = Resistor()

    write_output_to_log(t_vector, supply, storage, load)


if __name__ == "__main__":
    main()
