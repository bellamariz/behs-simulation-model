import csv
import pandas as pd
import matplotlib.pyplot as plt


# Main function to write the output of the simulation to a log file
def write_output_to_log(t_vector, supply, storage, load):
    with open("output.log", "w", encoding="utf-8") as logfile:
        print("Simulation started", file=logfile)
        for i, t in enumerate(t_vector):
            print(f"Time step {i}: t={t:.2f}s\n", file=logfile)

            supply.refresh(t_index=i)
            supply.print(t_index=i, file=logfile)

            storage.refresh(t_time=t, v_supply=supply.voltage,
                            load_energy_consumed=load.energy_consumed)
            storage.print(t_index=i, file=logfile)

            load.refresh(v_supply=storage.voltage,
                         v_load_min=storage.V_LOAD_MIN)
            load.print(t_index=i, file=logfile)

            print("-" * 50, file=logfile)


# Main function to write the output of the simulation to a CSV file
def write_output_to_csv(t_vector, supply, storage, load):
    with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["step", "time", "component", "voltage", "current",
                      "energy_stored", "energy_consumed", "total_energy_consumed"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, t in enumerate(t_vector):
            supply.refresh(t_index=i)
            storage.refresh(t_time=t, v_supply=supply.voltage,
                            load_energy_consumed=load.energy_consumed)
            load.refresh(v_supply=storage.voltage,
                         v_load_min=storage.V_LOAD_MIN)

            writer.writerow({
                "step": i,
                "time": t,
                "component": "supply",
                "voltage": supply.voltage,
                "current": "NaN",
                "energy_stored": "NaN",
                "energy_consumed": "NaN",
                "total_energy_consumed": "NaN",
            })
            writer.writerow({
                "step": i,
                "time": t,
                "component": "storage",
                "voltage": storage.voltage,
                "current": storage.current,
                "energy_stored": storage.energy_stored,
                "energy_consumed": "NaN",
                "total_energy_consumed": "NaN",
            })
            writer.writerow({
                "step": i,
                "time": t,
                "component": "load",
                "voltage": load.voltage,
                "current": load.current,
                "energy_stored": "NaN",
                "energy_consumed": load.energy_consumed,
                "total_energy_consumed": load.total_energy_consumed
            })


# Main function to write the output of the simulation to an Excel file
def write_output_to_excel():
    df = pd.read_csv("output.csv")
    df.to_excel("output.xlsx", index=False, na_rep="NaN")


# Main function to plot the simulation output
# Reads data from Excel file 'output.xlsx'
def plot_output():
    df = pd.read_excel("output.xlsx")
    components = ["supply", "storage", "load"]

    # Plot same attribute for all components, in the same subplot and window
    plot_all_components_same_subplot(
        df, components, ["voltage", "V"])
    plt.show()

    # Plot same attribute for all components, in separate subplots, but same window
    plot_all_components_different_subplots(
        df, components, ["voltage", "V"])
    plt.show()

    # Plot all attributes for a component, in separate subplots, but same window
    plot_all_attributes_for_component(
        df, components[1], [["voltage", "V"], ["current", "A"], ["energy_stored", "J"]])
    plt.show()

    plot_all_attributes_for_component(
        df, components[2], [["voltage", "V"], ["current", "A"], ["total_energy_consumed", "J"]])
    plt.show()


# Plots the same attribute over time for all components, overlapped on the same subplot
# Useful for comparing the same attribute across different components
# Param 'y_attribute' is a list of attribute name and unit, e.g. ["voltage", "V"]
def plot_all_components_same_subplot(df, components, y_attribute):
    value = y_attribute[0]
    unit = y_attribute[1]

    plt.figure(figsize=(10, 6))

    for component in components:
        comp_df = df[df["component"] == component]
        plt.plot(comp_df["time"], comp_df[value], label=component)

    plt.title(f"{value.capitalize()} ({unit}) x Time (s)")
    plt.xlabel("Time (s)")
    plt.ylabel(f"{value.capitalize()} ({unit})")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    return plt


# Plots the same attribute over time for all components, but in different subplots
# Useful for comparing the same attribute across different components
# Param 'y_attribute' is a list of attribute name and unit, e.g. ["voltage", "V"]
def plot_all_components_different_subplots(df, components, y_attribute):
    _, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True, sharey=True)

    value = y_attribute[0]
    unit = y_attribute[1]

    for ax, component in zip(axes, components):
        comp_df = df[df["component"] == component]
        ax.plot(comp_df["time"], comp_df[value], label=component)
        ax.set_title(f"{value.capitalize()} ({unit}) x Time (s)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(f"{value.capitalize()} ({unit})")
        ax.grid(True)
        ax.legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])


# Plots all attributes for a specific component in the same window
# Useful for visualizing multiple attributes of a single component over time
# Param 'y_attributes' is a list of sub-lists containing attribute name and unit
# e.g. [["voltage", "V"], ["current", "A"]]
def plot_all_attributes_for_component(df, component, y_attributes):
    _, axes = plt.subplots(1, len(y_attributes), figsize=(
        6 * len(y_attributes), 5), sharex=True)

    if len(y_attributes) == 1:
        axes = [axes]

    for ax, y_attribute in zip(axes, y_attributes):
        value = y_attribute[0]
        unit = y_attribute[1]

        comp_df = df[df["component"] == component]
        ax.plot(comp_df["time"], comp_df[value], label=component)
        ax.set_title(f"{value.capitalize()} ({unit}) x Time (s)")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel(f"{value.capitalize()} ({unit})")
        ax.grid(True)
        ax.legend()

    plt.suptitle("Attributes of " + component.capitalize() +
                 " Over Time", fontsize=16)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
