# BEHS Simulation Model

A Python-based simulation model for Battery-less Energy Harvesting Systems.

# Modules

## Energy Storage

The **Energy Storage** module (`energy_storage.py`) defines the `EnergyStorage` class, which simulates an energy storage component for Battery-less Energy Harvesting Systems (BEHS).

Its class methods include:

- `charge(number)` - Adds energy to storage.
- `discharge(amount)` - Removes energy from storage.
- `get_energy_level` - Get currently stored energy.
- `get_capacity` - Get maximum storage capacity.

### Usage

```python
from src.energy_storage import EnergyStorage

# Create an energy storage with a capacity of 100 units
storage = EnergyStorage(capacity=100)

# Add energy
storage.charge(20)

# Remove energy
storage.discharge(10)

# Check current energy level
print("current storage: %d" % storage.get_energy_level()) 
```
