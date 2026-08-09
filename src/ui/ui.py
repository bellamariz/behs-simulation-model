import tkinter as tk
from tkinter import ttk, messagebox


class SimulationForm:
    def __init__(self):
        self._result = None
        self._vars = {}
        self._dynamic_frames = {}

        self._root = tk.Tk()
        self._root.title("Battery-less Energy Harvesting System Simulator")
        self._root.resizable(True, True)

        self._apply_style()
        self._build()

    def _apply_style(self):
        self._root.configure(bg="#1c3a5e")
        style = ttk.Style(self._root)
        style.theme_use("clam")
        style.configure(".", background="#1c3a5e", foreground="white",
                        font=("Arial", 10))
        style.configure("TFrame", background="#1c3a5e")
        style.configure("TLabel", background="#1c3a5e", foreground="white")
        style.configure("TLabelframe", background="#1c3a5e",
                        foreground="white", bordercolor="#4a7fc1")
        style.configure("TLabelframe.Label", background="#1c3a5e",
                        foreground="white", font=("Arial", 11, "bold"))
        style.configure("TEntry", fieldbackground="#2d5a8e", foreground="white",
                        insertcolor="white")
        style.configure("TCombobox", fieldbackground="#2d5a8e",
                        foreground="white", selectbackground="#3a7bc8")
        style.map("TCombobox", fieldbackground=[("readonly", "#2d5a8e")])
        style.configure("TButton", background="#3a7bc8", foreground="white",
                        font=("Arial", 10, "bold"))
        style.map("TButton", background=[("active", "#4a8fd8")])

    def _build(self):
        # Button bar is packed first so it anchors to the bottom regardless of
        # scroll content changes — avoids buttons being displaced when dynamic
        # frames are re-packed inside the scrollable area.
        btn_frame = ttk.Frame(self._root)
        btn_frame.pack(side="bottom", fill="x", padx=12, pady=12)
        ttk.Button(btn_frame, text="Run Simulation",
                   command=self._on_run).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="Cancel",
                   command=self._on_cancel).pack(side="left")

        container = ttk.Frame(self._root)
        container.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(container, bg="#1c3a5e", highlightthickness=0,
                                 width=520)
        scrollbar = ttk.Scrollbar(container, orient="vertical",
                                  command=self._canvas.yview)
        self._scroll_frame = ttk.Frame(self._canvas)

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all"))
        )
        self._canvas.create_window((0, 0), window=self._scroll_frame,
                                   anchor="nw")
        self._canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)
        self._canvas.bind("<Enter>", lambda _: self._canvas.bind_all(
            "<MouseWheel>", self._on_mousewheel))
        self._canvas.bind(
            "<Leave>", lambda _: self._canvas.unbind_all("<MouseWheel>"))

        f = self._scroll_frame
        ttk.Label(f, text="Simulation Configuration",
                  font=("Arial", 14, "bold")).pack(anchor="w", padx=12,
                                                   pady=(12, 4))

        self._build_simulation_frame(f)
        self._build_supply_frame(f)
        self._build_storage_frame(f)
        self._build_load_frame(f)
        self._build_actions_frame(f)

    def _on_mousewheel(self, event):
        delta = event.delta
        if abs(delta) >= 120:
            delta = delta // 120
        self._canvas.yview_scroll(-delta, "units")

    def _refresh_scroll(self):
        self._canvas.update_idletasks()
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _var(self, key, default=""):
        var = tk.StringVar(value=default)
        self._vars[key] = var
        return var

    def _add_field(self, parent, label_text, key, default, entry_width=14):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=6, pady=2)
        ttk.Label(row, text=label_text, width=30, anchor="w").pack(side="left")
        ttk.Entry(row, textvariable=self._var(key, default),
                  width=entry_width).pack(side="left")
        return row

    def _add_combo(self, parent, label_text, key, options, default):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=6, pady=2)
        ttk.Label(row, text=label_text, width=30, anchor="w").pack(side="left")
        var = tk.StringVar(value=default)
        self._vars[key] = var
        combo = ttk.Combobox(row, textvariable=var, values=options,
                             state="readonly", width=16)
        combo.pack(side="left")
        return combo

    def _build_simulation_frame(self, parent):
        lf = ttk.LabelFrame(parent, text="Time Parameters", padding=6)
        lf.pack(fill="x", padx=12, pady=5)
        self._add_field(lf, "Duration (s):", "sim_duration", "120")
        self._add_field(lf, "Step (s):", "sim_step", "0.25")

    def _build_supply_frame(self, parent):
        lf = ttk.LabelFrame(parent, text="Supply", padding=6)
        lf.pack(fill="x", padx=12, pady=5)

        combo = self._add_combo(lf, "Type:", "supply_type",
                                ["constant", "harvesting"], "constant")

        const_frame = ttk.Frame(lf)
        const_frame.pack(fill="x")
        self._add_field(const_frame, "Base Power Output (W):",
                        "supply_p_base", "0.05")
        self._dynamic_frames["supply_constant"] = const_frame

        harv_frame = ttk.Frame(lf)
        self._add_field(harv_frame, "Filename:", "supply_filename", "",
                        entry_width=30)
        self._add_field(harv_frame, "Sampling Period (s):",
                        "supply_sampling_period", "2")
        self._dynamic_frames["supply_harvesting"] = harv_frame
        harv_frame.pack_forget()

        combo.bind("<<ComboboxSelected>>",
                   lambda _: self._on_supply_type_change())

    def _build_storage_frame(self, parent):
        lf = ttk.LabelFrame(parent, text="Storage", padding=6)
        lf.pack(fill="x", padx=12, pady=5)

        self._add_combo(lf, "Type:", "storage_type",
                        ["capacitor"], "capacitor")
        self._add_field(lf, "Capacitance (F):", "storage_capacitance", "0.1")
        self._add_field(lf, "Max Operating Voltage (V):",
                        "storage_v_oper_max", "5.5")

    def _build_load_frame(self, parent):
        lf = ttk.LabelFrame(parent, text="Load", padding=6)
        lf.pack(fill="x", padx=12, pady=5)

        combo = self._add_combo(lf, "Type:", "load_type",
                                ["resistor", "mcu"], "mcu")

        resistor_frame = ttk.Frame(lf)
        self._add_field(resistor_frame, "Resistance (Ohms):",
                        "load_resistance", "1600")
        self._add_field(resistor_frame, "Power Rating (W):",
                        "load_p_rating", "0.25")
        self._add_field(resistor_frame, "Max Voltage (V):",
                        "load_v_max", "5.5")
        self._dynamic_frames["load_resistor"] = resistor_frame
        resistor_frame.pack_forget()

        mcu_frame = ttk.Frame(lf)
        mcu_frame.pack(fill="x")
        self._add_field(mcu_frame, "Min Voltage (V):", "load_v_min", "1.8")
        self._add_field(mcu_frame, "Wake-up Voltage (V):",
                        "load_v_wake_up", "2")
        self._add_field(mcu_frame, "Low Power Op. Voltage (V):",
                        "load_v_oper_low", "2.2")
        self._add_field(mcu_frame, "Active Op. Voltage (V):",
                        "load_v_oper_active", "3.0")
        self._add_field(mcu_frame, "Max Voltage (V):",
                        "load_v_max", "3.6")

        modes_frame = ttk.Frame(mcu_frame)
        modes_frame.pack(fill="x", pady=(6, 2))
        ttk.Label(modes_frame, text="Consumption Current (A)",
                  font=("Arial", 10), foreground="white").pack(
                      anchor="w", padx=6, pady=(0, 2))
        sub_frame = ttk.Frame(modes_frame)
        sub_frame.pack(fill="x", padx=(30, 0))
        self._add_field(sub_frame, "Shutdown Mode:",
                        "load_mode_shutdown", "0")
        self._add_field(sub_frame, "Low-Power Mode:",
                        "load_mode_low_power", "0.000092")
        self._add_field(sub_frame, "Active Mode:",
                        "load_mode_active", "0.00048")

        self._add_field(mcu_frame, "Program Script:", "load_program",
                        "src/input/files/program01.script", entry_width=30)
        self._dynamic_frames["load_mcu"] = mcu_frame

        combo.bind("<<ComboboxSelected>>",
                   lambda _: self._on_load_type_change())

    def _build_actions_frame(self, parent):
        lf = ttk.LabelFrame(parent, text="Actions", padding=6)
        self._dynamic_frames["actions"] = lf
        lf.pack(fill="x", padx=12, pady=5)

        header = ttk.Frame(lf)
        header.pack(fill="x", padx=6, pady=(0, 2))
        ttk.Label(header, text="Action", width=14, anchor="w",
                  font=("Arial", 10, "bold")).pack(side="left")
        ttk.Label(header, text="Instruction", width=14, anchor="w",
                  font=("Arial", 10, "bold")).pack(side="left")
        ttk.Label(header, text="Cost (A)", width=14, anchor="w",
                  font=("Arial", 10, "bold")).pack(side="left")

        actions = [
            ("Sleeping:", "action_sleep_instr", "SLEEP",
             "action_sleep_cost", "0.00012"),
            ("Sensing:", "action_sense_instr", "SENSE",
             "action_sense_cost", "0.006"),
            ("Transmitting:", "action_tx_instr", "TX_ON",
             "action_tx_cost", "0.03"),
            ("Receiving:", "action_rx_instr", "RX_ON",
             "action_rx_cost", "0.027"),
            ("Processing:", "action_proc_instr", "CPU_PROC",
             "action_proc_cost", "0"),
        ]
        for label, instr_key, instr_default, cost_key, cost_default in actions:
            row = ttk.Frame(lf)
            row.pack(fill="x", padx=6, pady=1)
            ttk.Label(row, text=label, width=14, anchor="w").pack(side="left")
            ttk.Entry(row, textvariable=self._var(instr_key, instr_default),
                      width=12).pack(side="left", padx=(0, 4))
            ttk.Entry(row, textvariable=self._var(cost_key, cost_default),
                      width=12).pack(side="left")

    def _on_supply_type_change(self):
        is_constant = self._vars["supply_type"].get() == "constant"
        if is_constant:
            self._dynamic_frames["supply_harvesting"].pack_forget()
            self._dynamic_frames["supply_constant"].pack(fill="x")
        else:
            self._dynamic_frames["supply_constant"].pack_forget()
            self._dynamic_frames["supply_harvesting"].pack(fill="x")
        self._refresh_scroll()

    def _on_load_type_change(self):
        is_mcu = self._vars["load_type"].get() == "mcu"
        if is_mcu:
            self._dynamic_frames["load_resistor"].pack_forget()
            self._dynamic_frames["load_mcu"].pack(fill="x")
            self._dynamic_frames["actions"].pack(fill="x", padx=12, pady=5)
        else:
            self._dynamic_frames["load_mcu"].pack_forget()
            self._dynamic_frames["actions"].pack_forget()
            self._dynamic_frames["load_resistor"].pack(fill="x")
        self._refresh_scroll()

    def _on_run(self):
        self._result = {key: var.get() for key, var in self._vars.items()}
        self._root.quit()

    def _on_cancel(self):
        self._result = None
        self._root.quit()

    def run(self):
        self._root.mainloop()
        self._root.destroy()
        return self._result


def build_input_form():
    return SimulationForm()
