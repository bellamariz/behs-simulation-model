# BEHS Simulation Model

# Description

> _**Warning:** The project is still under ongoing improvements. The equations that model system components might change in the future._

Our project provides a simulation framework for analyzing and understanding the energy behaviour of **Battery-less Energy Harvesting Systems** (BEHS).

It was designed to help researchers and professionals in the field of IoT who study and develop energy harvesting applications, such as wireless sensor networks, environmental monitoring systems, wearable electronics, etc.

Users can use the implemented abstract classes inside the `src` folder to simulate a BEHS application. They can extend these classes to define their own components for the system: an energy supply, an energy storage and a load. They can run simulations for different components combinations, and plot graphs to observe the energetic behavior of each sub-system.

The following methods are available on `main.py`:

- `generate_t_vector()` - Generates a time vector with a given start, end and interval times.

The following methods are available on module `output.py`:

- `write_to_log()` - Runs simulation and writes output to local log file, `output.log`.
- `write_to_csv()` - Runs simulation and writes output to local CSV file, `output.csv`.
- `write_to_excel()` - Reads CSV file and writes output to local Excel file, `output.xlsx`.
- `plot()` - Reads Excel file and plots the output.
   - It provides three default types of plotting methods.
   - Users can update the file to create their own, and add them to the `plot()` method.

# System Scenarios

## Positive Scenario A

A researcher configures the simulation model to compare different energy sources for a wireless temperature monitoring system. 

The first application uses a solar panel as the energy supply, a supercapacitor as the storage, and a microcontroller (MCU) as the load. The time window is a 24-hour simulation with an interval of 1 minute. The goal is to observe daily solar energy cycles. 

For example, the results show that during the day (with constant voltage), the supercapacitor charges efficiently and powers the MCU correctly. Visualization graphs display the MCU's average energy consumption in constrast to the supercapacitor's capacity. This may help to determine the best supercapacitor size needed for operating the application at night. 

Next, the researcher tests a wind energy harvester and compares the output with the solar harvester. This may help them select the optimal energy source for their system.

## Positive Scenario B

A student wants to analyze how different load configurations may impact the same energy storage. 

Using the simulation model, they implement a custom load component by inheriting from the Load base class.
They simulate voltage, current and energy consumption values for an MCU with peripherals, that periodically wakes, measures data, transmits it, and returns to sleep.

By changing the voltage, current and energy consumption values (i.e. changing for how long the MCU sleeps or sends the data) for different simulations, the user can compare the different outputs and graphs. The results show how differing loads's energy consumption affected the capacitor charging and discharing cycles. 

This may help the student select a suitable storage component for their configured load.

## Negative Scenario A

A researcher wants to simulate a system with a solar panel and a wind turbine generator working together as the total energy supply.

But, when they try to run the output functions in `main.py`, passing two energy supply components as parameters, they realise the code doesn't work. This happens because, as of now, the simulation only supports one supply, one storage, and one load at a time to generate the log and CSV files. 

```python
# Writes output of simulation to local log file, 'output.log'
output.write_to_log(t_vector, supply, storage, load)

# Formats and writes output to local CSV file, 'output.csv'
output.write_to_csv(t_vector, supply, storage, load)
```

The researcher realizes that to run the simulation with multiple components of the same type would require updating a lot of the core code.

In the end, they have to run the simulation twice (once for each supply) and combine the results themselves, which is a lot more work.

## Negative Scenario B

A student attempts to simulate a wireless sensor node that periodically transmits data and then enters a deep sleep mode, drawing very little current from the capacitor energy storage. 

They notice that, the capacitor charges and discharges normally until it reaches the minimum operating voltage needed for supplying the load. With every following time step, the capacitor's energy, voltage and current levels oscilate considerably, increasing above the min load threshold and falling below it. This happens because the current implementation does not accurately deduct the load's energy consumption from the storage's energy, especially with rapid state changes. 

As a result, the simulation produces innacurate results, making it difficult to evaluate how long the storage can support the load or how to best configure the storage component correctly. 

The student realizes that the energy deduction logic between the load and storage needs to be revised to ensure realistic energy transfer and accurate simulation outcomes.

# Technical Documentation

## About

The project is built on a Python (>= 3.13) framework, and to compile it correctly, we recommend that users run the code using a Python virtual environment. Learn more about how to install and activate a virtual environment for your operating system [here](https://realpython.com/python-virtual-environments-a-primer/).

## BEHS Architecture

A **Battery-less Energy Harvesting System** (BEHS) is an IoT-based solution normally destined towards battery-less and/or low-power applications. It harvests natural energy sources from the environment to power its end-use computational devices and electronics.

A BEHS can be decomposed into three sub-systems:

- The *Harvesting Circuit* captures ambient energy and converts it into electrical energy (e.g. solar, wind, mechanical).
- The *Energy Storage* stores excess energy for later use by the system (e.g. capacitors).
- The *Load* is the device being powered (e.g. microcontroller, peripherals).

![Energy Harvesting Architecture](docs/eh-architecture.png)

## Project Architecture

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

On the `main.py` module, users can instantiate these components and generate a time vector using the `generate_t_vector()` function. 

The `output.py` module allows users to study the simulation output. The simulation is run by the `write_to_log()` and `write_to_csv` functions, which write the simulation data to local log/CSV files. Then, the dataset is parsed to an Excel file by the `write_to_excel` function, which will be read by the `plot()` function to plot the graphs with the data.

This will allow users to observe and understand the energetic behaviour of the system and its components over time. 

```python
def main():
    # Generates a time vector
    t_vector = generate_t_vector(start=0, end=60, interval=0.25)

    # Initializes the components of the simulation
    supply = ConstantSupply(t_vector)
    storage = Capacitor()
    load = Resistor()

    # Run simulation and write output to local log file, 'output.log'
    output.write_to_log(t_vector, supply, storage, load)

    # Run simulation and write output to local CSV file, 'output.csv'
    output.write_to_csv(t_vector, supply, storage, load)

    # Formats CSV and writes output to local Excel file, 'output.xlsx'
    output.write_to_excel()

    # Reads Excel file and plots the output
    output.plot()
```

## Class Diagram

The BEHS simulation model is structured according to the class diagram below.

![Class Diagram for project.](/docs/class-diagram.png)

The Mermaid code for the diagram can be found [here](/docs/class-diagram-mermaid.md).

### Abstract Component Classes

1. **EnergySupply**: Represents the harvested energy sources that provide power to the system.
   - Defines an interface for voltage supply and energy profile.
   - Supports both constant and variable energy sources.
   - Default components already implemented: `ConstantSupply()` and `HarvestingSupply()`.

2. **EnergyStorage**: Represents energy storage components like capacitors
   - Manages energy buffering between supply and consumption
   - Handles charging/discharging cycles and energy calculations

3. **Load**: Represents energy-consuming components in the system
   - Defines minimum operating voltages and energy consumption patterns
   - Tracks cumulative energy consumption over time

### Implemented Component Classes

1. Inheriting **EnergySupply**, we have:
   - **ConstantSupply**: Provides constant supply of 8V.
   - **HarvestingSupply**: Provides variable supply (0 to MAX_SUPPLY_VOLTAGE), simulating ambient energy sources.

2. Inheriting **EnergyStorage**, we have:
   - **Capacitor**: Assumes an RC circuit model for the charging/discharging equations.
      - Includes safety thresholds (V_STORAGE_MAX, V_LOAD_MIN).
      - Models realistic capacitor behavior with time constants.

3. Inheriting **Load**, we have:
   - **Resistor**: Simple resistor with fixed RESISTANCE and OPERATING_VOLTAGE, and a constant power consumption (ENERGY_CONSUMPTION).
   - **MCU**: Microcontroller with specific operating requirements (OPERATING_VOLTAGE, OPERATING_CURRENT), and a constant power consumption (ENERGY_CONSUMPTION).

### System Integration

The **Main** class handles the simulation by:
- Instantiating system components.
- Creating a time vector for temporal analysis.
- Controlling the simulation start and output.

The **Output** class handles data export and visualization by:
- Exporting the simulation to log, CSV, and Excel files.
- Creating multiple plot types for analysis.
- Supporting customizable visualization options.


# User Guide

## Installation and Setup

For setting up instructions, check the [README.md](../README.md).

## Complete Usage

>_Make sure all dependencies are installed and your Python virtual environment is configured before continuing._

### Running Default Simulation

**Task:** Execute a simulation with default components, time window and data plotting.

**Steps:**
1. Open the project in your preferred IDE.
2. Active the Python virtual environment.
3. Make sure all dependencies are installed.
4. Run the simulation:
   ```sh
   make run
   ```
5. The simulation will generate three output files.
   - `output.log` - Detailed log file.
   - `output.csv` - CSV format data.
   - `output.xlsx` - Excel format data.
6. Four graph windows will be displayed:
    - Graph for voltage over time for all components, on the same subplot.
    - Graph for voltage over time for all components, on different subplots side-by-side.
    - Graph for multiple attributes over time for the default `storage` component, i.e. capacitor.
    - Graph for multiple attributes over time for the default `load` component, i.e. resistor.

### Customizing Simulation Time Window

**Task:** Customizing your simulation time window.

**Steps:**
1. Open the project in your preferred IDE.
2. Active the Python virtual environment.
3. Make sure all dependencies are installed.
4. Open file `main.py`.
5. Locate the `generate_t_vector` function call:
   ```python
   t_vector = generate_t_vector(start=0, end=60, interval=0.25)
   ```
6. Modify parameters:
   - `start`: Starting time (seconds).
   - `end`: Ending time (seconds). 
   - `interval`: Time step interval (seconds).
7. Save the file and run:
   ```sh
   make run
   ```
8. Running the simulation will produce the same file and graph outputs as Task 1's steps 5 and 6 (but with different values).

### Customizing Simulation Components

**Task:** Implementing your own components for the simulation.

**Steps:**
1. Open the project in your preferred IDE.
2. Active the Python virtual environment.
3. Make sure all dependencies are installed.
4. Navigate to the appropriate subfolder in `src`:
   - `supply/energy_supply.py` folder for energy supply components.
   - `storage/energy_storage.py` folder for energy storage components.
   - `load/load.py` folder for load components.
5. Create a new class for your new component, and inherit from the base class:
   ```python
   from src.load.load import Load
   
   class MyNewLoad(Load):
       def __init__(self):
           # Your implementation
           pass
   ```
6. Implement all required abstract methods from the base class.
7. Import and use your component in `main.py`:
   ```python
   from src.load.load import MyNewLoad
   load = MyNewLoad()
   ```
8. Run the simulation again, and don't forget to create a new test suite inside the `tests` folder for your new class.

### Customizing Simulation Output Plotting

**Task:** Customizing which components and their attributes are plotted in simulation results.

**Explaining the attributes:**
The generated Excel file (`output.xlsx`) will have the columns below, which will be used for plotting:
  - `step`: Simulation time index.
  - `time`: Actual time value (seconds).
  - `component`: Component type (`supply`/`storage`/`load`).
  - `voltage`: Voltage value (Volts).
  - `current`: Current value (Amperes).
  - `energy_stored`: Energy stored (Joules) - only applicable to `storage` component.
  - `energy_consumed`: Energy consumed (Joules) - only applicable to `load` component.
  - `total_energy_consumed`: Cumulative energy consumed (Joules) - only applicable to `load` component.

**Steps:**
1. Open the project in your preferred IDE.
2. Active the Python virtual environment.
3. Make sure all dependencies are installed.
4. Open `output.py` file and locate the `plot()` function.
5. Pass the desired parameters to one (or more) of the functions below and call them inside the `plot()` function:
    - `plot_all_components_same_subplot()` - plot same attribute for all components (same window and subplot).
    - `plot_all_components_different_subplots()` - plot same attribute for all components (same window but separate suplots).
    - `plot_all_attributes_for_component()` - plot all attributes for a given component (same window but separate suplots).
6. Save your changes and re-run the simulation:
  ```sh
  make run
  ```
7. The updated plots will be displayed.