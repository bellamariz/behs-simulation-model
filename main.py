from src.energy_storage import EnergyStorage

def main():
  # Create an energy storage with a capacity of 100 units
  storage = EnergyStorage(capacity=100)

  # Add energy
  storage.charge(20)

  # Remove energy
  storage.discharge(10)

  # Check current energy level
  print("current storage: %d" % storage.get_current_charge()) 

if __name__ == "__main__":
  main()