import time
from src.energy_storage import EnergyStorage


def main():
    # create energy storage of maximum voltage Vmax of 300V
    # considering an initial voltage supply Vin of 10V
    storage = EnergyStorage(vmax=300, vin=10)

    t_vector = [0.25, 0.5, 0.750, 1, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75,
                3, 3.25, 3.5, 3.75, 4.0, 4.25, 4.5, 4.75, 5, 5.25, 5.5, 5.75, 6]
    status_vector = ["charging"] * 25

    storage.print(0)

    for i, t in enumerate(t_vector):
        storage.refresh_energy_storage(
            t=t, vin=10, status=status_vector[i]
        )
        storage.print(t)
        time.sleep(1)


if __name__ == "__main__":
    main()
