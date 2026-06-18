# Simulation Input Configuration File

This document describes how to prepare the configuration file [input.json](/src/input/files/input.json) that will be loaded into the simulator.

## 1. Simulation Parameters

The `simulation` configuration parameters are as follows.

| Parameter | Type | Description |
|---|---|---|
| **duration** | `float` | Total simulation duration (in seconds). |
| **interval** | `float` | Simulation step (in seconds). |
| **steps** | `int` | Total amount of simulation steps (**duration** / **interval**). |

For example:

```json
{
  "simulation": {
    "duration": 120,
    "interval": 0.25,
    "steps": 480
  }
}
```

## 2. BEHS Parameters

### 2.1. Energy Supply

The following `EnergySupply` types are available.

#### 2.1.1 Constant (Generic)

The `ConstantSupply` class represents a constant energy profile as the energy supply.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of supply, value is `"constant"`. |
| **v_base** | `float` | Base value for constant voltage supply. |

For example:

```json
{
  "supply":{
    "type": "constant",
    "v_base": 8.0
  }
}
```

This will generate a **profile** attribute for the `ConstantSupply` class, which is a vector of size **steps**, where each simulation step will assume a supply voltage of **v_base**.

#### 2.1.2 Harvesting (Generic)

The `HarvestingSupply` class represents a variable energy profile, non-specific to any harvesting device, as the energy supply.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of supply, value is `"constant"`. |
| **filename** | `string` | Path to the text file that contains the energy supply profile. |

For example:

```json
{
  "supply":{
    "type": "harvesting",
    "filename": "src/input/files/solar-data.txt",
  }
}
```

The user MUST include a text file that contains the normalized energy profile measurements gathered from a real Energy Harvesting source. There must be a supply voltage value for each simulation step. For example, for 60 second simulation with steps of 0.25s, the text file must include an energy profile matching this same period (i.e. 240 values, one for each step).

Public datasets of real Energy Harvesting measurements are readily available online, for example, [Long-Term Tracing of Indoor Solar Harvesting](https://zenodo.org/records/3363925).

The normalized data will be loaded into the **profile** attribute of the `HarvestingSupply` class, which is a vector of size **steps**, where each simulation step will assume the supply voltage configured in the **filename** text file for that step.


### 2.2. Energy Storage

The following `EnergyStorage` types are available.

#### 2.2.1 Capacitor

The `Capacitor` storage class represents a double-layer capacitor as an energy storage.

The configuration parameters are as follows.

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of storage, value is `"capacitor"`. |
| **capacitance** | `float` | Capacitance value of capacitor (in F). |
| **v_oper_max** | `float` | Maximum operating voltage (in Volts). |
| **i_supply_max** | `float` | Maximum supply current (in Amperes). |
| **r_charge** | `float` | Charging resistance (in Ohms). | 

These values can be easily acquired from the capacitor datasheet. For example, for the [FTW0H104ZF](https://www.digikey.com.br/en/products/detail/kemet/FTW0H104ZF/4290862) capacitor, we have:

```json
{
  "storage": {
    "type": "capacitor",
    "capacitance": 0.1,
    "v_oper_max": 5.5,
    "i_supply_max": 0.05,
    "r_charge": 510
  }
}
```

## 2.3 Load

The following `Load` types are available.

### 2.3.1. Resistor (Generic)

The `Resistor` class represents a single IoT device with constant energy consumption.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of supply, value is `"resistor"`. |
| **resistance** | `float` | Resistance value (in Ohms). |
| **p_rating** | `float` | Resistor power rating (in Watts). |
| **v_load_min** | `float` | Mininum storage voltage necessary for load to "begin" consuming energy. |

For example, if considering an actual resistor [CF14JT1K60 1.6kOhms](https://www.digikey.com.br/en/products/detail/stackpole-electronics-inc/CF14JT1K60/1741251), we have the following:

```json
{
  "load": {
    "type": "resistor",
    "resistance": 1600,
    "p_rating": 0.25,
    "v_load_min": 1.2
  }
}
```

It represents a load that consumes a constant amount of energy over time.

### 2.3.2. MCU (Generic)

The `MCU` class represents a single IoT device with variable energy consumption.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of supply, value is `"mcu"`. |
| **v_min** | `float` | Minimum operating voltage. |
| **v_wake_up** | `float` | Minimum voltage necessary to wake-up the MCU from `"shutdown"`. |
| **v_oper_low** | `float` | Nominal operating voltage for `"low_power"` mode. |
| **v_oper_active** | `float` | Nominal operating voltage for `"active"` mode. |
| **v_max** | `float` | Maximum operating voltage. |
| **clock** | `string` | Clock frequency for the CPU, will influence the energy cost for each operating mode. |
| **modes** | `dict` | List of CPU operating modes and their energy cost (in A) - cost for `"active"` mode depends on the clock frequency. |
| **program** | `string` | Path to the script file that represents software being executed by the MCU. |

For example, if using a [TI MSP430FR5994](https://www.ti.com/lit/ds/slase54d/slase54d.pdf?ts=1781671720297) MCU, with [configurable power modes](https://www.ti.com/lit/ug/tiduc02/tiduc02.pdf?ts=1781611206249), the configuration is:

```json
{
  "load": {
    "type": "mcu",
    "v_min": 1.8,
    "v_wake_up": 2,
    "v_oper_low": 2.2,
    "v_oper_active": 3.0,
    "v_max": 3.6,
    "clock": "4MHZ",
    "modes": {
      "shutdown": 0,
      "low_power": 0.000092,
      "active": {
        "1MHz": 0.000120,
        "4MHz": 0.000480,
        "8MHz": 0.000960,
        "12MHz": 0.001440,
        "16MHz": 0.001920,
      },
    },
    "program": "src/input/files/program01.script",
  }
}
```

The `MCU` class represents a load that collects, processes and trasmits data. The simulator considers two types of operations to calculate the consumed energy: CPU and tasks. For CPU, consumption depends on the current power mode and the configured clock frequency. For tasks, the simulator provides a default list of actions, each with their own estimated power consumption.

```json
{
  "actions": [
    {
      "action": "sleeping",
      "instruction": "SLEEP",
      "cost": 0.00003
    },
    {
      "action": "sensing",
      "instruction": "SENSE",
      "cost": 0.006
    },
    {
      "action": "transmitting",
      "instruction": "TX_ON",
      "cost": 0.03
    },
    {
      "action": "receiving",
      "instruction": "RX_ON",
      "cost": 0.027
    },
    {
      "action": "processing",
      "instruction": "CPU_PROC",
    }
  ]
}
```

Lastly, the user MUST include at least ONE new script file that contains the program sequence (i.e. list of tasks) that will be executed by the MCU (**program** file). This script file will represent the CPU and task operations over the simulation window, emulating real software.

Each line of the script must be an instruction, followed by the time it took in milliseconds. For example:

```txt
LOOP
  SLEEP 1000
  SENSE 2500
  CPU_PROC
  TX_ON 5000
END
```

Considering a simulation step of 250ms, and a CPU on `"active"` mode and a clock of 4MHz, for example, this script translates to:

| # | Instruction | Duration (ms) | Cost (mA) |
|---|---|---|---|
| 0 | `SLEEP` | 1000 | 0.012 |
| 0 | `SENSE` | 2500 | 60 |
| 0 | `CPU_PROC` | ~10 clocks | 4.8 |
| 0 | `TX_ON` | 5000 | 600 |

Where the total cost of each instruction is calculated by `(duration / t_step) * cost` - with except for the CPU operation, which is `#clocks * cost`.
