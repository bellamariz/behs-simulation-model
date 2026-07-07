def run(sim_input):
    if sim_input == {}:
        raise ValueError("Simulation input cannot be empty!")

    # Extract simulation parameters
    t_step = sim_input.t_step
    t_vector = sim_input.t_vector

    # For each time t in the simulation, refresh values for:
    #   1. Energy Supply        - Update energy supplied at time t.
    #   2. Load                 - Update energy consumed at time t, based on v_supply at (t-1).
    #   3. PMIC (if applicable) - Update v_out and vbat_ok, based on v_storage at (t-1).
    #                           - Update energy_to_storage and energy_from_storage at time t.
    #   4. Energy Storage       - Update energy stored at time t.
    sim_output = {}
    for i, t in enumerate(t_vector):
        sim_input.supply.refresh(t_index=i, t_step=t_step)

        # Mode 1: (Supply -> Storage <- Load)
        # Storage is directly connected to the Supply and Load
        if sim_input.pmic is None:
            sim_input.load.refresh(
                v_supply=sim_input.storage.voltage, t_step=t_step)
            sim_input.storage.refresh(
                e_supply=sim_input.supply.energy_supply,
                e_load=sim_input.load.energy_consumed,
                t_step=t_step
            )
        # Mode 2: (Supply -> PMIC -> Storage <- Load)
        # We use a PMIC to manage the energy flow between the Supply, Storage, and Load
        else:
            sim_input.load.refresh(
                v_supply=sim_input.pmic.v_out, t_step=t_step)
            sim_input.pmic.refresh(
                e_supply=sim_input.supply.energy_supply,
                e_load=sim_input.load.energy_consumed,
                v_storage=sim_input.storage.voltage,
                t_step=t_step
            )
            sim_input.storage.refresh(
                e_supply=sim_input.pmic.energy_to_storage,
                e_load=sim_input.pmic.energy_from_storage,
                t_step=t_step
            )

        sim_output[t] = {
            "supply": {
                "type": sim_input.supply.type,
                "power_supply": sim_input.supply.power_supply,
                "energy_supply": sim_input.supply.energy_supply,
            },
            "storage": {
                "type": sim_input.storage.type,
                "status": sim_input.storage.status,
                "voltage": sim_input.storage.voltage,
                "current": sim_input.storage.current,
                "energy_stored": sim_input.storage.energy_stored,
                "power_stored": sim_input.storage.power_stored,
            },
            "load": {
                "type": sim_input.load.type,
                "mode": sim_input.load.mode,
                "voltage": sim_input.load.voltage,
                "current": sim_input.load.current,
                "energy_consumed": sim_input.load.energy_consumed,
                "total_energy_consumed": sim_input.load.total_energy_consumed,
            },
        }

        if sim_input.load.program is not None:
            sim_output[t]["load"]["program_executed_ops"] = list(
                sim_input.load.program.executed_ops_last_step)

        if sim_input.pmic is not None:
            sim_output[t]["pmic"] = {
                "type": sim_input.pmic.type,
                "status": sim_input.pmic.status,
                "vout": sim_input.pmic.v_out,
                "vbat_ok": sim_input.pmic.vbat_ok,
                "energy_to_storage": sim_input.pmic.energy_to_storage,
                "energy_from_storage": sim_input.pmic.energy_from_storage,
            }

    return sim_output
