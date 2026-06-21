import PySimpleGUI as sg

sg.theme("DarkBlue2")


def build_input_form():
    layout = [
        [sg.Text("Simulation Configuration", font=("Arial", 14, "bold"))],

        # Simulation parameters
        [sg.Frame("Time Parameters", font=("Arial", 12, "bold"), layout=[
            [sg.Text("Duration (s):"), sg.InputText(
                "120", key="sim_duration", size=(10,))],
            [sg.Text("Step (s):"), sg.InputText(
                "0.25", key="sim_step", size=(10,))],
        ])],

        # Supply configuration
        [sg.Frame("Supply", font=("Arial", 12, "bold"), layout=[
            [sg.Text("Type:"), sg.Combo(["constant", "harvesting"],
                                        default_value="constant", key="supply_type",
                                        enable_events=True)],
            [sg.Column([
                [sg.Text("Base Voltage (V):"), sg.InputText(
                    "8.0", key="supply_v_base", size=(10,))],
            ], key="col_supply_constant", visible=True)],
            [sg.Column([
                [sg.Text("Filename:"), sg.InputText(
                    "", key="supply_filename", size=(35,))],
                [sg.Text("Sampling Period (s):"), sg.InputText(
                    "2", key="supply_sampling_period", size=(10,))],
            ], key="col_supply_harvesting", visible=False)],
        ])],

        # Storage configuration
        [sg.Frame("Storage", font=("Arial", 12, "bold"), layout=[
            [sg.Text("Type:"), sg.Combo(["capacitor"],
                                        default_value="capacitor", key="storage_type")],
            [sg.Text("Capacitance (F):"), sg.InputText(
                "0.1", key="storage_capacitance", size=(10,))],
            [sg.Text("Max Operating Voltage (V):"), sg.InputText(
                "5.5", key="storage_v_oper_max", size=(10,))],
            [sg.Text("Series Resistance (Ohms):"), sg.InputText(
                "510", key="storage_r_charge", size=(10,))],
        ])],

        # Load configuration
        [sg.Frame("Load", font=("Arial", 12, "bold"), layout=[
            [sg.Text("Type:"), sg.Combo(["resistor", "mcu"],
                                        default_value="mcu", key="load_type",
                                        enable_events=True)],
            [sg.Column([
                [sg.Text("Resistance (Ohms):"), sg.InputText(
                    "1600", key="load_resistance", size=(10,))],
                [sg.Text("Power Rating (W):"), sg.InputText(
                    "0.25", key="load_p_rating", size=(10,))],
            ], key="col_load_resistor", visible=False)],
            [sg.Column([
                [sg.Text("Min Voltage (V):"), sg.InputText(
                    "1.8", key="load_v_min", size=(10,))],
                [sg.Text("Wake-up Voltage (V):"), sg.InputText("2",
                                                               key="load_v_wake_up", size=(10,))],
                [sg.Text("Low Power Op. Voltage (V):"), sg.InputText(
                    "2.2", key="load_v_oper_low", size=(10,))],
                [sg.Text("Active Op. Voltage (V):"), sg.InputText(
                    "3.0", key="load_v_oper_active", size=(10,))],
                [sg.Text("Max Voltage (V):"), sg.InputText(
                    "3.6", key="load_v_max", size=(10,))],
                [sg.Text("Shutdown Current (A):"), sg.InputText(
                    "0", key="mode_shutdown", size=(10,))],
                [sg.Text("Low Power Current (A):"), sg.InputText(
                    "0.000092", key="mode_low_power", size=(10,))],
                [sg.Text("Active Current (A):"), sg.InputText(
                    "0.00048", key="mode_active", size=(10,))],
                [sg.Text("Program Script:"), sg.InputText(
                    "src/input/files/program01.script", key="load_program", size=(35,))],
            ], key="col_load_mcu", visible=True)],
        ])],

        # Actions configuration (MCU only)
        [sg.Column([
            [sg.Frame("Actions", font=("Arial", 12, "bold"), layout=[
                [sg.Text("Action", size=(12, 1)), sg.Text(
                    "Instruction", size=(12, 1)), sg.Text("Cost (A)", size=(12, 1))],
                [sg.Text("Sleeping:", size=(12, 1)), sg.InputText("SLEEP", key="action_sleep_instr", size=(
                    12,)), sg.InputText("0.00012", key="action_sleep_cost", size=(12,))],
                [sg.Text("Sensing:", size=(12, 1)), sg.InputText("SENSE", key="action_sense_instr", size=(
                    12,)), sg.InputText("0.006", key="action_sense_cost", size=(12,))],
                [sg.Text("Transmitting:", size=(12, 1)), sg.InputText("TX_ON", key="action_tx_instr", size=(
                    12,)), sg.InputText("0.03", key="action_tx_cost", size=(12,))],
                [sg.Text("Receiving:", size=(12, 1)), sg.InputText("RX_ON", key="action_rx_instr", size=(
                    12,)), sg.InputText("0.027", key="action_rx_cost", size=(12,))],
                [sg.Text("Processing:", size=(12, 1)), sg.InputText("CPU_PROC", key="action_proc_instr", size=(
                    12,)), sg.InputText("0", key="action_proc_cost", size=(12,))],
            ])],
        ], key="col_actions", visible=True)],

        [sg.Button("Run Simulation"), sg.Button("Cancel")]
    ]

    window = sg.Window("BEHS Simulation", layout, finalize=True)
    return window


def handle_ui_events(window, event, values):
    """Update element visibility based on type selection events."""
    if event == "supply_type":
        is_constant = values["supply_type"] == "constant"
        window["col_supply_constant"].update(visible=is_constant)
        window["col_supply_harvesting"].update(visible=not is_constant)

    if event == "load_type":
        is_mcu = values["load_type"] == "mcu"
        window["col_load_resistor"].update(visible=not is_mcu)
        window["col_load_mcu"].update(visible=is_mcu)
        window["col_actions"].update(visible=is_mcu)
