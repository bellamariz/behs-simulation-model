import src.simulator.simulator as simulator
import src.output.output as out
import src.input.input as inp
import src.interface.interface as ui
import src.eh.eh as eh
from tkinter import messagebox


def run_manual():
    # Initializes the simulation input configuration
    config = inp.load_config_from_file(inp.CONFIG_FILE_PATH)

    # Uncomment to generate "profile_filepath" file for EnergySupply (when applicable)
    # File only needs to be generated once, and can be reused for all simulations.
    # inp.set_up_eh_supply_profile_file(config.get("supply"))

    sim_input = inp.Input(config)

    # Run simulation for given input params
    sim_output = simulator.run(sim_input)

    # Write output to local log file, 'output.log'
    out.write_to_log(sim_output)

    # Write output to local CSV file, 'output.csv'
    out.write_to_csv(sim_output)

    # Formats CSV and writes output to local Excel file, 'output.xlsx'
    out.write_to_excel()

    # Reads Excel file and plots the output
    out.plot()


def run_ui():
    form = ui.build_input_form()
    values = form.run()

    if values is None:
        return

    try:
        config = inp.load_config_from_ui(values)

        # Initializes the simulation input configuration
        sim_input = inp.Input(config)

        # Run simulation for given input params
        sim_output = simulator.run(sim_input)
        messagebox.showinfo("Success", "Simulation run successfully!")

        # Write output to local log file, 'output.log'
        out.write_to_log(sim_output)

        # Write output to local CSV file, 'output.csv'
        out.write_to_csv(sim_output)

        # Formats CSV and writes output to local Excel file, 'output.xlsx'
        out.write_to_excel()

        # Reads Excel file and plots the output
        out.plot()

    except Exception as e:
        messagebox.showerror("Error", f"Error: {str(e)}")


def main():
    # Uncomment the line below to run the simulation with a manual configuration
    run_manual()

    # TODO: Update interface to consider new simulation UI
    # Uncomment the line below to run the simulation with a UI for input configuration
    # run_ui()


if __name__ == "__main__":
    main()
