from src.energy_storage import EnergyStorage


def main():
    # Create an energy storage with a capacity of 100 units
    storage = EnergyStorage(capacity=100)

    # Add energy
    storage.charge(20)

    # Remove energy
    storage.discharge(10)

    # Check current energy level
    print(f"current storage: {storage.get_energy_level()}")


if __name__ == "__main__":
    main()
