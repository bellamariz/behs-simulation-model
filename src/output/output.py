import csv
import pandas as pd
import matplotlib.pyplot as plt


# Main function to write the output of the simulation to a log file
def write_to_log(sim_output):
    with open("output.log", "w", encoding="utf-8") as logfile:
        print("Simulation started", file=logfile)
        for t, data in sim_output.items():
            print(f"Time step {t}: t={t:.3f}s\n", file=logfile)
            print(
                f"  Supply: type={data['supply']['type']}, energy={data['supply']['energy_supply']:.7f}J, power={data['supply']['power_supply']:.7f}W", file=logfile)
            print(
                f"  Load: type={data['load']['type']}, status={data['load']['mode']}, voltage={data['load']['voltage']:.5f}V, current={data['load']['current']:.7f}A, energy={data['load']['energy_consumed']:.7f}J, total_energy_consumed={data['load']['total_energy_consumed']:.7f}J", file=logfile)
            if data['load']['program_executed_ops']:
                ops_str = ", ".join(
                    f"{instruct}:{secs:.4f}s"
                    for instruct, secs in data['load']['program_executed_ops'].items()
                )
                print(f"  Program: ops=[{ops_str}]", file=logfile)
            if 'pmic' in data:
                print(
                    f"  PMIC: type={data['pmic']['type']}, status={data['pmic']['status']}, v_out={data['pmic']['vout']:.5f}V, vbat_ok={data['pmic']['vbat_ok']}, energy_to_storage={data['pmic']['energy_to_storage']:.7f}J, energy_from_storage={data['pmic']['energy_from_storage']:.7f}J", file=logfile)
            print(
                f"  Storage: type={data['storage']['type']}, status={data['storage']['status']}, voltage={data['storage']['voltage']:.5f}V, current={data['storage']['current']:.7f}A, energy={data['storage']['energy_stored']:.7f}J, power={data['storage']['power_stored']:.7f}W\n", file=logfile)
            print("-" * 50, file=logfile)


# Main function to write the output of the simulation to a CSV file
def write_to_csv(sim_output):
    with open("output.csv", "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["step", "time", "component", "status", "voltage", "current",
                      "energy", "power", "total_energy_consumed", "program_executed_ops"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for t, data in sim_output.items():
            program_executed_ops = "NaN"
            if data['load']['program_executed_ops']:
                program_executed_ops = ",".join(
                    f"{instruct}:{secs:.4f}s"
                    for instruct, secs in data['load']['program_executed_ops'].items()
                )

            writer.writerow({
                "step": t,
                "time": t,
                "component": "supply",
                "status": "NaN",
                "voltage": "NaN",
                "current": "NaN",
                "power": data['supply']['power_supply'],
                "energy": data['supply']['energy_supply'],
                "total_energy_consumed": "NaN",
                "program_executed_ops": program_executed_ops,
            })
            writer.writerow({
                "step": t,
                "time": t,
                "component": "storage",
                "status": data['storage']['status'],
                "voltage": data['storage']['voltage'],
                "current": data['storage']['current'],
                "power": data['storage']['power_stored'],
                "energy": data['storage']['energy_stored'],
                "total_energy_consumed": "NaN",
                "program_executed_ops": program_executed_ops,
            })
            writer.writerow({
                "step": t,
                "time": t,
                "component": "load",
                "status": data['load']['mode'],
                "voltage": data['load']['voltage'],
                "current": data['load']['current'],
                "power": "NaN",
                "energy": data['load']['energy_consumed'],
                "total_energy_consumed": data['load']['total_energy_consumed'],
                "program_executed_ops": program_executed_ops,
            })


# Main function to write the output of the simulation to an Excel file
def write_to_excel():
    df = pd.read_csv("output.csv", dtype={"program_executed_ops": str})
    df.to_excel("output.xlsx", index=False, na_rep="NaN")


# Main function to plot the simulation output
# Reads data from Excel file 'output.xlsx'
def plot():
    df = pd.read_excel("output.xlsx")
    components = ["supply", "storage", "load"]

    # Plot same attribute for all components, in the same subplot and window
    plot_all_components_same_subplot(
        df, components, ["energy", "J"])
    plt.show()

    plot_all_components_same_subplot(
        df, components, ["voltage", "V"])
    plt.show()

    # Plot same attribute for all components, in separate subplots, but same window
    # plot_all_components_different_subplots(
    #     df, components, ["energy", "J"])
    # plt.show()

    # Plot all attributes for a component, in separate subplots, but same window
    plot_all_attributes_for_component(
        df, components[0], [["power", "W"], ["energy", "J"]])
    plt.show()

    plot_all_attributes_for_component(
        df, components[1], [["voltage", "V"], ["energy", "J"]])
    plt.show()

    plot_all_attributes_for_component(
        df, components[2], [["voltage", "V"], ["energy", "J"], ["total_energy_consumed", "J"]])
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
