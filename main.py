from time import sleep
from src.storage.energy_storage import Capacitor
from src.supply.energy_supply import ConstantSupply
from src.load.load import Resistor
from internal.internal import Utils


def main():
    t_vector = Utils.generate_t_vector()
    supply = ConstantSupply(t_vector)
    storage = Capacitor()
    load = Resistor()

    for i, t in enumerate(t_vector):
        print(f"Time step {i}: t={t:.2f}s\n")

        supply.refresh(t_index=i)
        supply.print(t_index=i)

        storage.refresh(t_time=t, v_supply=supply.voltage)
        storage.print(t_index=i)

        load.refresh(v_supply=storage.voltage)
        load.print(t_index=i)

        print("-" * 50)

        sleep(2)


if __name__ == "__main__":
    main()
