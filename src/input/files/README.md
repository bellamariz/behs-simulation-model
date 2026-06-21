# Simulation Input Configuration File

This document describes how to prepare the configuration file [config.json](/src/input/files/config.json) that will be loaded into the simulator.

## 1. Simulation Parameters

The `simulation` configuration parameters are as follows.

| Parameter | Type | Description |
|---|---|---|
| **duration** | `float` | Total simulation duration (in seconds). |
| **step** | `float` | Simulation step (in seconds). |

For example:

```json
{
  "simulation": {
    "duration": 120,
    "step": 0.25
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
| **p_base** | `float` | Base power value for constant supply (in Watts). |

For example:

```json
{
  "supply":{
    "type": "constant",
    "p_base": 0.05
  }
}
```

This will generate a **profile** attribute for the `ConstantSupply` class, which is a vector of size **duration** / **step**. Each simulation step will estimate an energy supply value of **profile[t]** / **step**.

#### 2.1.2 Harvesting (Generic)

The `HarvestingSupply` class represents a variable energy profile, non-specific to any harvesting device, as the energy supply.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of supply, value is `"harvesting"`. |
| **filename** | `string` | Path to the text file that contains the energy supply dataset. |
| **sampling_period** | `float` | Sampling period of the energy dataset (in seconds). |

For example:

```json
{
  "supply":{
    "type": "harvesting",
    "filename": "src/input/files/solar-data.txt",
    "sampling_period": 2
  }
}
```

The user MUST include a text file containing the energy profile measurements gathered from a real Energy Harvesting source. The simulator will normalize this dataset from the provided **sampling_period** to the chosen simulation **step**.

Public datasets of real Energy Harvesting measurements are readily available online, for example, [Long-Term Tracing of Indoor Solar Harvesting](https://zenodo.org/records/3363925).

The normalized data will be loaded into the **profile** attribute of the `HarvestingSupply` class, which is a vector of size **duration** / **step**. Each simulation step will estimate an energy supply value of **profile[t]** / **step**.


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

These values can be easily acquired from the capacitor datasheet. For example, for the [FTW0H104ZF](https://www.digikey.com.br/en/products/detail/kemet/FTW0H104ZF/4290862) capacitor and a series resistance of 510 Ohm, we have:

```json
{
  "storage": {
    "type": "capacitor",
    "capacitance": 0.1,
    "v_oper_max": 5.5,
  }
}
```

### 2.3 Load

The following `Load` types are available.

#### 2.3.1. Resistor (Generic)

The `Resistor` class represents a single IoT device with constant energy consumption.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of load, value is `"resistor"`. |
| **resistance** | `float` | Resistance value (in Ohms). |
| **p_rating** | `float` | Resistor power rating (in Watts). |
| **v_max** | `float` | Maximum working voltage (in Voltz). |

For example, if considering an actual resistor [CF14JT1K60 1.6kOhms](https://www.digikey.com.br/en/products/detail/stackpole-electronics-inc/CF14JT1K60/1741251), we have the following:

```json
{
  "load": {
    "type": "resistor",
    "resistance": 1600,
    "p_rating": 0.25,
    "v_max": 250,
  }
}
```

It represents a load that consumes a constant amount of energy over each simulation **step**: `E(t) = (V^2/R)/step`.

#### 2.3.2. MCU (Generic)

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
| **modes** | `dict` | List of CPU operating modes and their energy cost (in A). |
| **program** | `string` | Path to the script file that represents software being executed by the MCU. |

For example, considering a [TI MSP430FR5994](https://www.ti.com/lit/ds/slase54d/slase54d.pdf?ts=1781671720297) MCU, with a 4Mhz clock and [configurable power modes](https://www.ti.com/lit/ug/tiduc02/tiduc02.pdf?ts=1781611206249), we have:

```json
{
  "load": {
    "type": "mcu",
    "v_min": 1.8,
    "v_wake_up": 2,
    "v_oper_low": 2.2,
    "v_oper_active": 3.0,
    "v_max": 3.6,
    "modes": {
      "shutdown": 0,
      "low_power": 0.000092,
      "active": 0.00048
    },
    "program": "src/input/files/program01.script"
  }
}
```

The `MCU` class represents a load that collects, processes and transmits data. The simulator considers two types of operations to calculate the consumed energy: CPU and tasks. For CPU, consumption depends on the current power mode and the configured clock frequency. For tasks, the simulator provides a default list of actions, each with their own estimated power consumption.

```json
{
  "actions": [
    {
      "action": "sleeping",
      "instruction": "SLEEP",
      "cost": 0.00012
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
      "cost": 0
    }
  ]
}
```

For the processing task (CPU_PROC), when the default cost in `"actions"` is zero, the simulator will use the CPU's operating mode's estimated cost (defined in **modes**)

Lastly, the user MUST include at least ONE new script file that contains the program sequence (i.e. list of tasks) that will be executed by the MCU (**program** file). This script file will represent the CPU and task operations over the simulation window, emulating real software.

Each line of the script must be an instruction, followed by the time it took in milliseconds. For example:

```txt
LOOP
  SLEEP 1000
  SENSE 2500
  CPU_PROC 100
  TX_ON 5000
END
```

Consider a simulation step of 250ms and an MCU class based on the MSP with the CPU on `"active"` mode and with clock of 4MHz, and a operating voltage of 3.0V. The program script above translates to the following energy consumption behaviour.

| # | Instruction | Duration (s) | Cost (A) | Charge (C) | Energy (J) |
|---|---|---|---|---|---|
| 0 | `SLEEP` | 1.0 = 4 steps | 0.00012 | 0.00012 | 0.00036 |
| 1 | `SENSE` | 2.5 = 10 steps | 0.006 | 0.015 |0.045 |
| 2 | `CPU_PROC` | 0.1 = 0.4 step | 0.00048 | 0.000048 | 0.000144 |
| 3 | `TX_ON` | 5.0 = 20 steps | 0.03 | 0.15 | 0.45 |

The total charge of each instruction is given by `Cost I(A) * Duration dt(s)` and the energy consumed is `Charge(C) * Voltage(V)`.

Over a simulation period of 35 steps (or 8.75s), the total energy consumed was 0.495504J.

## 3. Full Example Configuration File

```json
{
  "simulation": {
    "duration": 120,
    "step": 0.25
  },
  "supply":{
    "type": "constant",
    "p_base": 0.05
  },
  "storage": {
    "type": "capacitor",
    "capacitance": 0.1,
    "v_oper_max": 5.5,
  },
  "load": {
    "type": "mcu",
    "v_min": 1.8,
    "v_wake_up": 2,
    "v_oper_low": 2.2,
    "v_oper_active": 3.0,
    "v_max": 3.6,
    "modes": {
      "shutdown": 0,
      "low_power": 0.000092,
      "active": 0.00048
    },
    "program": "src/input/files/program01.script"
  },
  "actions": [
    {
      "action": "sleeping",
      "instruction": "SLEEP",
      "cost": 0.00012
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
      "cost": 0
    }
  ]
}
```
