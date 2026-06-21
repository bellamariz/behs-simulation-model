def run(sim_input):
    if sim_input == {}:
        raise ValueError("Simulation input cannot be empty!")

    # Extract simulation parameters
    t_step = sim_input.t_step
    t_vector = sim_input.t_vector

    # For each time t in the simulation:
    #   1. supply  — Compute energy supplied at time t
    #   2. load    — Compute energy consumed at time t, based on last storage state
    #   3. storage — Update storage state based on supply and load
    sim_output = {}
    for i, t in enumerate(t_vector):
        sim_input.supply.refresh(t_index=i, t_step=t_step)
        sim_input.load.refresh(
            v_supply=sim_input.storage.voltage, t_step=t_step)
        sim_input.storage.refresh(
            e_supply=sim_input.supply.energy_supply,
            e_load=sim_input.load.energy_consumed,
            t_step=t_step
        )

        sim_output[t] = {
            "supply": {
                "type": sim_input.supply.type,
                "power_output": sim_input.supply.power_output,
                "energy_supply": sim_input.supply.energy_supply,
            },
            "storage": {
                "type": sim_input.storage.type,
                "status": sim_input.storage.status,
                "voltage": sim_input.storage.voltage,
                "current": sim_input.storage.current,
                "energy_stored": sim_input.storage.energy_stored,
                "power_output": sim_input.storage.power_output,
            },
            "load": {
                "type": sim_input.load.type,
                "mode": sim_input.load.mode,
                "voltage": sim_input.load.voltage,
                "current": sim_input.load.current,
                "energy_consumed": sim_input.load.energy_consumed,
                "total_energy_consumed": sim_input.load.total_energy_consumed,
            }
        }

    return sim_output
