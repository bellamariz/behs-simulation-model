import time
import random
from src.energy_storage import EnergyStorage
from src.energy_supply import EnergySupply


def generate_t_vector():
    start = 0.0
    end = 6.0
    interval = 0.25
    return [start + i *
            interval for i in range(int((end - start) / interval) + 1)]


def generate_status_vector(t_vector):
    statuses = ["empty", "charging", "discharging", "full"]
    return [random.choice(statuses)
            for _ in range(len(t_vector))]


def main():
    t_vector = generate_t_vector()
    status_vector = generate_status_vector(t_vector)
    v_supply = EnergySupply("energy_neutral", t_vector)
    storage = EnergyStorage(vmax=10, vin=v_supply.profile[0])
    storage.print(0)

    for i, t in enumerate(t_vector):
        # storage.refresh_energy_storage(
        #     t=t, vin=v_supply_vector[i], status=status_vector[i]
        # )
        # storage.print(t)

        print(
            f"t={t},"
            f"v_supply={v_supply.profile[i]},"
            f"storage_status={status_vector[i]},"
        )
        time.sleep(1)


if __name__ == "__main__":
    main()
