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

## 2. Energy Harvesting System Parameters

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

For example, if considering an actual resistor [CF14JT1K60 1.6kOhms](https://www.digikey.com.br/en/products/detail/stackpole-electronics-inc/CF14JT1K60/1741251), the configuration is:

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

The `Resistor` class represents a load that consumes a constant amount of energy over each simulation step: `E(t) = (V^2/R) / t_step`.

#### 2.3.2. MCU (Generic)

The `MCU` class represents a single IoT device with variable energy consumption.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of supply, value is `"mcu"`. |
| **v_min** | `float` | Minimum operating voltage. |
| **v_wake_up** | `float` | Minimum voltage necessary to wake-up the MCU from `"shutdown"`. |
| **v_max** | `float` | Maximum operating voltage. |
| **modes** | `dict` | List of CPU operating modes, their energy cost (in A), clock frequency (in MHz) and operating voltage (in V). |
| **program** | `string` | Path to the script file that represents software being executed by the MCU. |

For example, if considering an actual MCU [Texas Instruments MSP430FR5994](https://www.ti.com/lit/ds/slase54d/slase54d.pdf?ts=1781671720297).

And making the following assumptions: 

- Operating temperature is 25ºC;
- Low-power mode is LPM1 (since we want power monitoring and interrupt capabilities);
- Clock is run at 16MHz on active mode (FRAM on);

The configuration is:

```json
{
  "load": {
    "type": "mcu",
    "v_min": 1.8,
    "v_wake_up": 2.0,
    "v_max": 3.6,
    "modes": {
      "standby": { "cost": 0.000001, "clock": 0.05, "v_oper": 2.2 },
      "active": { "cost": 0.001920, "clock": 16, "v_oper": 3.0 }
    }
  }
}
```

The `MCU` class represents a load that collects, processes and transmits data. The energy comsumption is modelled after two types of operations: tasks and CPU power state. The next section describes the available operations and their cost in detail.

# 3. Software Operations

When considering a Load of the `MCU` class, the simulation allows the user to define a program sequence (i.e. list of operations) that will be executed by this class, emulating real software applications.

The list of default available operations are:

| Type | Name | Code Instruction | Description | Cost (A)
|---|---|---|---|---|---|
| CPU | cpu_standby | `STANDBY` | CPU is in low-power mode | Depends on `MCU` **modes** |
| CPU | cpu_processing | `ACTIVE` | CPU is in active power mode | Depends on `MCU` **modes** |
| Task | sensing | `SENSE` | Reading sensor data | 0.006 |
| Task | transmitting | `TX` | Transmitting communication data | 0.03 |
| Task | receiving | `RX` | Receiving communication data | 0.027 |

> The Tasks and their costs are based on the work done by [Climent et al](https://onlinelibrary.wiley.com/doi/full/10.1002/cpe.3151).

The user MUST include a script file that defines the program sequence they wish to execute. Each line of the script must be an instruction followed by its execution time in seconds.

For example:

```txt
LOOP
  STANDBY 3
  SENSE 0.05
  ACTIVE 0.000070
  TX_ON 0.25
END
```

The path to this script file is included on the configuration file as well:

```json
{
  "program_file": "src/input/files/program01.txt"
}
```

The total charge of each instruction is given by `Cost I(A) * Duration dt(s)` and the energy consumed is `Charge(C) * Supply Voltage(V)`.

## 4. Example of Complete Configuration File

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
    "v_oper_max": 5.5
  },
  "load": {
    "type": "mcu",
    "v_min": 1.8,
    "v_wake_up": 2.0,
    "v_max": 3.6,
    "modes": {
      "standby": { "cost": 0.000001, "clock": 0.05, "v_oper": 2.2 },
      "active": { "cost": 0.001920, "clock": 16, "v_oper": 3.0 }
    }
  },
  "program_file": "src/input/files/program01.txt"
}
```
