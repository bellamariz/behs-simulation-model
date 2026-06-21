def run(sim_input):
    if sim_input == {}:
        raise ValueError("Simulation input cannot be empty!")

    t_vector = sim_input.t_vector
    sim_output = {}

    # Executes the simulation, updating the supply, storage and load at each time t
    for i, t in enumerate(t_vector):
        sim_input.supply.refresh(t_index=i)
        sim_input.storage.refresh(t_time=t, v_supply=sim_input.supply.voltage)
        sim_input.load.refresh(v_supply=sim_input.storage.voltage)

        sim_output[t] = {
            "supply": {
                "type": sim_input.supply.type,
                "voltage": sim_input.supply.voltage,
            },
            "storage": {
                "type": sim_input.storage.type,
                "status": sim_input.storage.status,
                "voltage": sim_input.storage.voltage,
                "current": sim_input.storage.current,
                "energy_stored": sim_input.storage.energy_stored,
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
