import PySimpleGUI as sg

sg.theme("DarkBlue2")


def build_input_form():
    layout = [
        [sg.Text("Simulation Configuration", font=("Arial", 14, "bold"))],

        # Supply configuration
        [sg.Frame("Supply", [
            [sg.Text("Type:"), sg.Combo(["constant", "harvesting"],
                                        default_value="constant", key="supply_type")]
        ])],

        # Storage configuration
        [sg.Frame("Storage", [
            [sg.Text("Type:"), sg.Combo(["capacitor"],
                                        default_value="capacitor", key="storage_type")]
        ])],

        # Load configuration
        [sg.Frame("Load", [
            [sg.Text("Type:"), sg.Combo(["resistor", "mcu"],
                                        default_value="resistor", key="load_type")]
        ])],

        # Time Vector configuration
        [sg.Frame("Time Vector", [
            [sg.Text("Start (s):"), sg.InputText(
                "0", key="t_start", size=(10,))],
            [sg.Text("End (s):"), sg.InputText("60", key="t_end", size=(10,))],
            [sg.Text("Interval (s):"), sg.InputText(
                "0.25", key="t_interval", size=(10,))]
        ])],

        [sg.Button("Run Simulation"), sg.Button("Cancel")]
    ]

    window = sg.Window("Simulation Setup", layout)
    return window


def get_config_from_ui(values):
    return {
        "supply": {"type": values["supply_type"]},
        "storage": {"type": values["storage_type"]},
        "load": {"type": values["load_type"]},
        "time": {
            "start": float(values["t_start"]),
            "end": float(values["t_end"]),
            "interval": float(values["t_interval"])
        }
    }
