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

    for i, t in enumerate(t_vector):
        print(f"Time step {i}: t={t:.2f}s\n")

        supply.refresh(t_index=i)
        supply.print(t_index=i)

        storage.refresh(t_time=t, v_supply=supply.voltage,
                        load_energy_consumed=load.energy_consumed)
        storage.print(t_index=i)

        load.refresh(v_supply=storage.voltage, v_load_min=storage.V_LOAD_MIN)
        load.print(t_index=i)

        print("-" * 50)


if __name__ == "__main__":
    main()
