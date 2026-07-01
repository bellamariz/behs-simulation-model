# Simulation Input Configuration File

This document describes how to prepare a configuration JSON file (`/src/input/files/config-*.json`) that will be loaded into the simulator.

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

This will generate a **profile** attribute for the `ConstantSupply` class, which is a vector of size **duration** / **step**. Each simulation step will estimate an energy supply value of: 

$$E(t) =  \frac{profile[t]}{t_{\text{step}}}$$

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

The normalized data will be loaded into the **profile** attribute of the `HarvestingSupply` class, which is a vector of size **duration** / **step**. Each simulation step will estimate an energy supply value of:

$$E(t) =  \frac{profile[t]}{t_{\text{step}}}$$

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

The `Capacitor` has the following operational states:

- **"empty"** - if the energy storage is empty.
- **"charging"** - if more energy is being supplied than consumed.
- **"discharging"** - if more energy is being consumed than supplied.
- **"idle"** - if energy supply and consumption are equal.
- **"full"** - if energy storage reaches its maximum capacity, `E_MAX`.

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

For example, if considering an actual resistor [CF14JT10K0 10kOhms](hhttps://www.digikey.com/en/products/detail/stackpole-electronics-inc/CF14JT10K0/1741265), the configuration is:

```json
{
  "load": {
    "type": "resistor",
    "resistance": 10000,
    "p_rating": 0.5,
    "v_max": 350,
  }
}
```

The `Resistor` class represents a load that consumes a constant amount of energy over each simulation step: 

$$E = \frac{V^2}{R} \times t_{\text{step}}$$

#### 2.3.2. MCU (Generic)

The `MCU` class represents a single IoT device with variable energy consumption.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of supply, value is `"mcu"`. |
| **v_min** | `float` | Minimum operating voltage. |
| **v_max** | `float` | Maximum operating voltage. |
| **modes** | `dict` | List of CPU operating modes, their energy cost (in A), clock frequency (in MHz) and operating voltage (in V). |
| **program** | `string` | Path to the script file that represents software being executed by the MCU. |

For example, if considering an actual MCU [Texas Instruments MSP430FR5994](https://www.ti.com/lit/ds/slase54d/slase54d.pdf?ts=1781671720297).

We have the following operating modes:

- **"active"** - Active mode; CPU is on; maximum current consumption; all features are available; executes any programmed software.
- **"standby"** - Low-power mode; CPU is sleeping; current consumption is low; many features still available (wake-up/interrupt events, data retention and some peripherals).
- **"shutdown"** - Shutdown mode; CPU is off; minimal current consumption; only supply voltage supervisor is available.

By assuming the following information from the *MSP430FR5994* datasheet:

- Operating temperature is 25ºC;
- Chosen standby mode is LPM2 (includes supply voltage supervisor and interrupt capabilities);
- Chosen shutdown mode is LPM4.5 (includes supply voltage supervisor); 
- Clock is running at 16MHz on active mode with FRAM on.

The `MCU` configuration is:

```json
{
  "load": {
    "type": "mcu",
    "v_min": 1.8,
    "v_max": 3.6,
    "modes": {
      "shutdown": { "cost": 0.0000003, "clock": 0.0, "v_oper": 2.0 },
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

| Type | Name | Code Instruction | Description | Cost (A) |
|---|---|---|---|---|
| CPU | cpu_standby | `STANDBY` | CPU is in low-power mode | Depends on `MCU` **modes** |
| CPU | cpu_processing | `ACTIVE` | CPU is in active power mode | Depends on `MCU` **modes** |
| Task | loop_start | `LOOP` | Indicates a loop start | 0 |
| Task | loop_end | `END` | Indicates a loop end | 0 |
| Task | sensing | `SENSE` | Reading sensor data | 0.006 |
| Task | transmitting | `TX` | Transmitting communication data | 0.03 |
| Task | receiving | `RX` | Receiving communication data | 0.027 |

> The sensing, transmitting and receiving tasks are based on the work done by [Climent et al](https://onlinelibrary.wiley.com/doi/full/10.1002/cpe.3151).

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

## 4. PMIC: Power Management Integrated Circuit

An `PMIC` component can be configured between the **Supply**, **Storage** and **Load**, to control the energy flow of the system more appropriately.

- **Input (Supply ---> Storage):** a boost charger draws energy from the harvesting supply and charges the storage.
- **Output (Storage ---> Load):** a buck converter draws energy from the storage and supplies load with a fixed voltage.

It has the following operating modes:

- **"cold_start"** - start charging **Storage** using a cold-start circuit, but buck converter is off (i.e. **Load** is not consuming).
- **"boost_only"** - start charging **Storage** using normal boost charger, but buck converter is off.
- **"charging"** - energy flowing into **Storage** is greater than energy flowing out, buck converter is on (i.e. **Load** is consuming).
- **"discharging"** - energy flowing into **Storage** is less than energy flowing out, buck converter is on.
- **"idle"** - energy flowing into **Storage** equals energy flowing out, buck converter is on.
- **"full"** - stop charging **Storage** when it is full, buck converter is on, but boost charger is off.

This component is *optional*. 

If `"pmic"` is absent from the configuration JSON, the simulator falls back to the default connection model, where the raw storage voltage is supplied to the load.

The following `PMIC` types are available.

#### 2.4.1 BoostBuckPMIC

The `BoostBuckPMIC` class models an ultra-low-power energy harvesting PMIC.

It is based on the [Texas Instruments BQ25570](https://www.ti.com/product/BQ25570) integrated circuit.

The configuration parameters are:

| Parameter | Type | Description |
|---|---|---|
| **type** | `string` | Type of PMIC, value is `"boost_buck"`. |
| **v_in_cold_start** | `float` | Minimum harvesting supply voltage for `"cold-start"` charging mode to activate. |
| **v_boost_thresh** | `float` | The storage threshold voltage for the PMIC to switch from `"cold-start"` charging mode to `"boost_only"`charging mode. |
| **v_bat_uv** | `float` | The buck converter is disabled when storage voltage is equal or below this value, so the load does not receive power. |
| **v_bat_ov** | `float` | The boost charger is disabled when storage voltage is equal or above this value, so the storage stops charging. |
| **v_bat_ok_low** | `float` | When the storage is discharging and drops below this value, the `vbat_ok` attribute is *false*, warning the MCU that power is about to be lost. |
| **v_bat_ok_high** | `float` | When the storage is charging and rises above this value, the `vbat_ok` attribute is *true*, warning the MCU that it is safe to wake up and operate. |
| **v_out_reg** | `float` | The fixed voltage the buck converter delivers to the load (as long as the storage voltage is above **v_bat_uv**). |

The energy conversion between supply, storage and load is not always the most efficient, and energy can be lost during the conversion processes and when changing operating modes.

Additional parameters for the `PMIC` class can be defined by the user to account for the energy efficiency of the circuit:

| Parameter | Type | Description |
|---|---|---|
| **mppt_efficiency** | `float` | Fraction of the supply harvester's theoretical maximum power that the PMIC's algorithm can deliver (typically *0.80*). |
| **boost_efficiency** | `float` | Boost charger conversion efficiency between harvesting supply and storage (typically *0.70-0.90*). |
| **buck_efficiency** | `float` | Buck converter conversion efficiency between storage and load (typically between *0.85-0.93*). |
| **cold_start_efficiency** | `float` | Boost efficiency during cold-start, before the main charger is enabled (typical `0.50`). |

With these parameteres, the energy flow equations are:

$$E_{\text{to\_storage}} = E_{\text{supply}} \times \eta_{\text{mppt}} \times \eta_{\text{boost}}$$

$$E_{\text{from\_storage}} = \frac{E_{\text{load}}}{\eta_{\text{buck}}}$$

When applying the values from the *BQ25570* datasheet, the `PMIC` configuration is:

```json
{
  "pmic": {
    "type": "boost_buck",
    "v_in_cold_start": 0.6,
    "v_boost_thresh": 1.8,
    "v_bat_ov": 5.5,
    "v_bat_uv": 2.0,
    "v_bat_ok_low": 2.2,
    "v_bat_ok_high": 2.8,
    "v_out_reg": 3.3,
    "mppt_efficiency": 0.95,
    "boost_efficiency": 0.80,
    "buck_efficiency": 0.90,
    "cold_start_efficiency": 0.50
  }
}
```

## 4. Example of Complete Configuration File

```json
{
  "simulation": {
    "duration": 120,
    "step": 0.25
  },
  "supply":{
    "type": "harvesting",
    "sampling_period": 0.5,
    "profile_filepath": "src/eh/files/dataset-teg.csv"
  },
  "storage": {
    "type": "capacitor",
    "capacitance": 0.1,
    "v_oper_max": 5.5
  },
  "pmic": {
    "type": "boost_buck",
    "v_in_cold_start": 0.6,
    "v_boost_thresh": 1.8,
    "v_bat_ov": 5.5,
    "v_bat_uv": 2.0,
    "v_bat_ok_low": 2.2,
    "v_bat_ok_high": 2.8,
    "v_out_reg": 3.3,
    "mppt_efficiency": 0.95,
    "boost_efficiency": 0.80,
    "buck_efficiency": 0.90,
    "cold_start_efficiency": 0.50
  },
  "load": {
    "type": "mcu",
    "v_min": 1.8,
    "v_max": 3.6,
    "modes": {
      "shutdown": { "cost": 0.0000003, "clock": 0.0, "v_oper": 2.0 },
      "standby": { "cost": 0.000001, "clock": 0.05, "v_oper": 2.2 },
      "active": { "cost": 0.001920, "clock": 16, "v_oper": 3.0 }
    }
  },
  "program_filepath": "src/input/files/program01.txt"
}
```
