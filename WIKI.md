# BEHS Simulation Model

## Description

> _**Warning:** The project is still under ongoing improvements. The equations that model system components might change in the future._

Our project provides a simulation framework for analyzing and understanding the energy behaviour of **Battery-less Energy Harvesting Systems** (BEHS).

It was designed to help researchers and professionals in the field of IoT who study and develop energy harvesting applications, such as wireless sensor networks, environmental monitoring systems, wearable electronics, etc.

### BEHS Architecture

A **Battery-less Energy Harvesting System** (BEHS) is an IoT-based solution normally destined towards battery-less and/or low-power applications. It harvests natural energy sources from the environment to power its end-use computational devices and electronics.

A BEHS can be decomposed into three sub-systems:

- The *Harvesting Circuit* captures ambient energy and converts it into electrical energy (e.g. solar, wind, mechanical).
- The *Energy Storage* stores excess energy for later use by the system (e.g. capacitors).
- The *Load* is the device being powered (e.g. microcontroller, peripherals).

![Energy Harvesting Architecture](docs/eh-architecture.png)

Our proposed model allows users to define which components will comprise each sub-system. They can run simulations for different components combinations, and plot graphs to observe the energetic behavior of each sub-system.

### Usage

The `src` folder contains three sub-folders, one for each BEHS sub-system.

- `supply` - Represents the _Harvesting Circuit_ sub-system, implemented by the `EnergySupply` class.
- `storage` - Represents the _Energy Storage_ sub-system, implemented by the `EnergyStorage` class.
- `load` - Represents the _Load_ sub-system, implemented by the `Load` class.

This structure allows users to expand these inheritable classes and define new components of their own, for example:

```python
# Class Load for the BEHS simulation model
# It represents the load, a circuit component that consumes energy from the energy storage
class Load(ABC):
    @abstractmethod
    def __init__(self):
        ...

# Class Resistor for the BEHS simulation model, inheriting from Load Class
class Resistor(Load):
  ...

# Class MCU for the BEHS simulation model, inheriting from Load Class
class MCU(Load):
  ...

# Class ExternalCircuit for the BEHS simulation model, inheriting from Load Class
class ExternalCircuit(Load):
  ...
```

On the `main.py` module, users can instantiate these components, generate a time vector, and study the simulation output. This allows users to observe and understand the energetic behaviour of these components over time.

```python
def main():
    # Generates a time vector
    t_vector = generate_t_vector(start=0, end=60, interval=0.25)

    # Initializes the components of the simulation
    supply = ConstantSupply(t_vector)
    storage = Capacitor()
    load = Resistor()

    # Writes output of simulation to local log file, 'output.log'
    output.write_to_log(t_vector, supply, storage, load)

    # Formats and writes output to local CSV file, 'output.csv'
    output.write_to_csv(t_vector, supply, storage, load)

    # Formats and writes output to local Excel file, 'output.xlsx'
    output.write_to_excel()

    # Reads Excel file and plots the output
    output.plot()
```

The following methods are available on `main.py`:

- `generate_t_vector` - Generates a time vector with a given start, end and interval times.

The following methods are available on module `output.py`:

- `write_to_log` - Writes output of simulation to local log file, 'output.log'.
- `write_to_csv` - Formats and writes output to local CSV file, 'output.csv'.
- `write_to_excel` - Formats and writes output to local Excel file, 'output.xlsx'.
- `plot` - Reads Excel file and plots the output.

This module provides three types of output plotting methods, but users can update the file to create their own and then call them inside the main `plot` method.