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

Refer to the appropriate documentation file based on your needs.

- [**README.md**](../README.md) - Explains the initial setup for the repository and the available Makefile commands.
- [**CONFIGURATION.md**](/docs/CONFIGURATION.md) - Explains how to configure and customize the simulation input parameters.
- [**WIKI.md**](/docs/WIKI.md) - Comprehensive guide about the project, including the complete technical documentation and the user guide.

## Contributing

The intended use for this project is to help researchers and students to emulate EH applications and assist in early-stage system design.

However, as this is an open-source project, we encourage and support any community contributions! Feel free to report bugs, recommend improvements and implement new features. Repository mantainers are keeping an eye on opened issues and pull requests.

The recommended workflow for contributions is through [forking](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project), in cause you don't have permission to make changes directly. 

If you do plan to clone and push directly to the repository, make sure to follow these instructions.

1. Create a new branch to work on. Branching from `main` is allowed.
2. Follow the code style of the project, including indentation and in-code comments.
3. Always keep the tests and documentation updated as you make changes.
4. Commit messages are recommended to follow the [conventional commits](https://www.conventionalcommits.org/en/v1.0.0/) syntax.
5. When opening a PR, use the template available [here](.github/workflows/pull_request_template.md). Review and approval from other contributors is recommended, but not mandatory. We suggest avoiding AI reviewers on PRs, e.g. Copilot.
6. Before merging a PR into `main`, check if the `pylint` and `pytest` workflow jobs have passed. Also, we highly recommend squashing your commits. It helps to keep the repository's commit history clean.

## License

Released under the [MIT License](/LICENSE).