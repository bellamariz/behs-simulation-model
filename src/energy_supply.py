import random

# There are three energy supply profiles:
#
# 1- Energy Neutral:
#     The harvested energy is equal to or exceeds the energy consumed by the system over time.
#     Energy storage is normally used to buffer differences in supply and demand during smaller periods
# 2- Power Neutral:
#     Assumes a zero-storage approach and works under the premise that the energy generated equals the energy consumed.
#     Controls its performance by adapting computer processes to match the energy levels.
# 3- Intermittent Energy:
#     Systems where the power requirements exceed the maximum amount of energy the harvester or storage are capable of supplying.
#     Periods of active operation are mixed with periods for recharging the energy storage.


class EnergySupply:
    MAX_SUPPLY_VOLTAGE = 5.5  # assumes max supply voltage of 5.5V

    def __init__(self, operation_mode, t_vector):
        self.operation_mode = operation_mode
        self.profile = [random.uniform(0.0, self.MAX_SUPPLY_VOLTAGE)
                        for _ in range(len(t_vector))]

    def print(self, t_vector):
        print(f"operation_mode={self.operation_mode}")
        for i, t in t_vector:
            print(
                f"t={t},"
                f"Vs(t={t})={self.profile[i]:.4f}\n,"
            )
