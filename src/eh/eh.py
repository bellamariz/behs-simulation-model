# Package used to parse EH datasets and extract relevant data for simulation

import h5py
import pandas as pd
import numpy as np


# Parser class for a TEG Energy Harvester dataset in HDF5 format.
# Variable(s) of interest:
# - boost_ichg_ua: charging current output of the LTC3108 boost converter model
#
# Source DOI: https://dl.acm.org/doi/10.1145/3485730.3494111
# Dataset: https://dataverse.lib.virginia.edu/dataset.xhtml?persistentId=doi:10.18130/V3/M9CP9C
class TEGDataHDF5Parser:
    INPUT_FILEPATH = "src/eh/files/TP001_env1.h5"

    def __init__(self, output_filepath):
        self.V_OUT = 3.3  # output voltage (V) of the LTC3108 boost converter
        self.SAMPLING_PERIOD = 0.5  # in seconds

        self.output_filepath = output_filepath
        self.df = self._parse_to_dataframe()
        self.duration = self.df.index[-1] - self.df.index[0]

    # Parses the HDF5 dataset into a useable pandas dataframe
    def _parse_to_dataframe(self):
        with h5py.File(self.INPUT_FILEPATH, "r") as f:
            key = list(f.keys())[0]
            g = f[key]

            # Timestamps
            index_raw = g["axis1"][:]
            timestamps = pd.to_datetime(index_raw, unit="ns", utc=True)

            # block 0 - floats
            b0_cols = [c.decode() if isinstance(c, bytes)
                       else c for c in g["block0_items"][:]]
            b0_vals = g["block0_values"][:]
            df0 = pd.DataFrame(b0_vals, index=timestamps, columns=b0_cols)

            # block_1 - booleans/flags
            b1_cols = [c.decode() if isinstance(c, bytes)
                       else c for c in g["block1_items"][:]]
            b1_vals = g["block1_values"][:]
            df1 = pd.DataFrame(b1_vals, index=timestamps, columns=b1_cols)

            df = pd.concat([df0, df1], axis=1)

        df.index.name = "timestamp"

        return df

    # Prints the parsed dataframe
    def print_dataframe(self):
        print(self.df.columns.tolist())
        print(self.df.head())
        print(f"Shape: {self.df.shape}")
        print(f"Duration: {self.duration}")

    # Parses the output metrics and relevant dataframes for the dataset
    def parse_output(self):
        # Remove invalid rows
        # - flag_thermocouple_invalid: temperature sensor was not working correctly
        # - flag_teg_disconnected: TEG was disconnected from the LTC3108 boost converter
        df_valid = self.df[
            (self.df["flag_thermocouple_invalid"] == 0) &
            (self.df["flag_teg_disconnected"] == 0)
        ].copy()

        # Charging current output values from uA to A
        df_valid["i_out_a"] = df_valid["boost_ichg_ua"] * 0.000001
        mean_output_current = df_valid["i_out_a"].mean()

        # Power output at each timestep (Watts)
        df_valid["power_out_w"] = df_valid["i_out_a"] * self.V_OUT
        mean_output_power = df_valid["power_out_w"].mean()

        # Energy output per sampling period (Joules)
        df_valid["energy_per_sp_j"] = df_valid["power_out_w"] * \
            self.SAMPLING_PERIOD

        # Cumulative harvested energy over time (Joules)
        df_valid["energy_cumulative_j"] = df_valid["energy_per_sp_j"].cumsum()
        total_harvested_energy = df_valid['energy_cumulative_j'].iloc[-1]

        output = {
            "dataframes": {
                "i_out_a": df_valid['i_out_a'],
                "power_out_w": df_valid['power_out_w'],
                "energy_per_sp_j": df_valid['energy_per_sp_j'],
                "energy_cumulative_j": df_valid['energy_cumulative_j']
            },
            "metrics": {
                "mean_output_power_w": mean_output_power,
                "mean_charging_current_a": mean_output_current,
                "total_harvested_energy_j": total_harvested_energy,
                "duration": self.duration,
            }
        }

        return output

    # Prints the generated output
    def print_output(self, output):
        metrics = output['metrics']
        print(
            f"Mean output power: {metrics['mean_output_power_w']:.6f} W")
        print(
            f"Mean charging current: {metrics['mean_charging_current_a']:.6f} A")
        print(
            f"Total harvested energy: {metrics['total_harvested_energy_j']:.6f} J")
        print(
            f"Duration: {metrics['duration']}")

    def write_output_to_csv(self, output):
        df = pd.DataFrame(output['dataframes'])
        df.to_csv(self.output_filepath, index=True)


# Calls TEGDataHDF5Parser class
def teg_dataset_to_csv(output_filepath):
    parser = TEGDataHDF5Parser(output_filepath)
    output = parser.parse_output()
    parser.print_output(output)
    parser.write_output_to_csv(output)
