# BEHS Simulation Model

A Python-based simulation model for Battery-less Energy Harvesting Systems (BEHSs).

## Description

This model may be used to simulate and trace the energy flowing across the BEHS over time. 

Given a group of pre-configured input parameters (i.e. input energy profile and energy storage architecture), we can compute the energy consumption of the system over an established time period.

The [Jupyter Notebook](Model.ipynb) present in this repository further explains the simulation model and features complete usage examples for this project.

## Getting Started

The `Makefile` contains all necessary commands for installing dependencies and running the simulation.

```sh
make lint    # Run pylint for linting the code
make test    # Run pytest for testing
make install # Install dependencies from requirements.txt
make run     # Run the simulation
make clean   # Clean up all cache files
```
