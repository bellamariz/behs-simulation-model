# BEHS Simulation Model

A Python-based simulation model for Battery-less Energy Harvesting Systems (BEHSs).

## Description

This model may be used to simulate and trace the energy flowing across a Battery-less Energy Harvesting System (BEHS) over time. 

Given a group of pre-configured input parameters (e.g. energy supply, energy storage and load), we can visualize the energy behaviour of the system over an established time period.

## Getting Started

> *Make sure you are using a **Python virtual environment** to run the project. Learn more about how to install and activate a virtual environment for your operating system [here](https://realpython.com/python-virtual-environments-a-primer/).*

Download the project `.zip` or use Git clone, like below:

```sh
git clone https://github.com/bellamariz/behs-simulation-model.git
```

Inside the project directory, the `Makefile` contains all necessary commands for running the project features.

### Install dependencies

The project dependencies are listed in the local file `requirements.txt`. To install them, run:

```sh
make install
```

### Run tests

To execute the test suites, run:

```sh
make test
```

### Run code linter

To execute the Python code linter, run:

```sh
make lint
```

### Run simulation

To execute the simulation model, run:

```sh
make run
```

Output to CLI when executing the simulation.

![Simulation output to terminal.](/docs/pictures/simulation_stdout.png)

Output plot example of energy over time for all BEHS components.

![Plot example of all components energy x time.](/docs/pictures/output_plot_example.png)

Output plot example of a harvesting supply component's attributes over time.

![Plot example of supply attributes x time.](/docs/pictures/output_plot_example2.png)

Output plot example of a microcontroller load components's attributes over time.

![Plot example of load attributes x time.](/docs/pictures/output_plot_example3.png)


### Cleaning cached files

By default, Python generates several cache files after running code, tests or linter. To clean these cached files, run:

```sh
make clean
```

## Documentation

Full project documentation, including the User Guide, can be found on the [docs](docs/) folder.