# BEHS Simulation Model

A Python-based simulation model for Battery-less Energy Harvesting Systems (BEHSs).

## Description

This model may be used to simulate and trace the energy flowing across a Battery-less Energy Harvesting System (BEHS) over time. 

Given a group of pre-configured input parameters (e.g. energy supply, energy storage and load), we can visualize the energy behaviour of the system over an established time period.

## Getting Started

The `Makefile` contains all necessary commands for mantaining the project.

> *Make sure you are using a **Python virtual environment** to run these commands. Learn more about how to install and activate a virtual environment for your operating system [here](https://realpython.com/python-virtual-environments-a-primer/).*

### Installing dependencies

The project dependencies are listed in the local file `requirements.txt`. To install them, run:

```sh
make install
```

### Running

To execute the simulation model at `main.py`, run:

```sh
make run
```

### Code Linter

To execute a code linter using `pylint`, run:

```sh
make lint
```

### Tests

To execute all test suites using `pytest`, run:

```sh
make test
```

### Cleaning cache files

By default, Python generates several cache files after running code, tests or linter. To clean these cached files, run:

```sh
make clean
```