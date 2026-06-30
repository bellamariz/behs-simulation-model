from abc import ABC, abstractmethod


# Class PMIC for the BEHS simulation model
# It represents a Power Management IC (PMIC) that controls the energy flow of the BEHS system.
#
# The PMIC model manages the energy input and output of the Energy Storage element.
#   - Input: Supply -> Storage (boost charger)
#   - Output: Storage -> Load (regulated buck converter)
class PMIC(ABC):
    @abstractmethod
    def __init__(self):
        self.type: str
        self.status: str                 # current operating mode of the PMIC
        self.v_out: float                # output voltage (V) supplied to Load
        self.vbat_ok: bool               # if Storage is ok for Load operation
        self.energy_to_storage: float    # energy supplied (J) to Storage
        self.energy_from_storage: float  # energy consumed (J) from Storage

    # Updates the VBAT_OK flag indicating to the Load if the Storage is ok for operation.
    @abstractmethod
    def update_vbat_ok_signal(self, v_storage: float) -> bool:
        pass

    # Calculates the output voltage delivered to the load.
    @abstractmethod
    def calculate_v_out(self, v_storage: float) -> float:
        pass

    # Calculates energy transferred from Supply into Storage (boost charger).
    @abstractmethod
    def calculate_energy_supplied_to_storage(self, e_supply: float, v_storage: float) -> float:
        pass

    # Calculates energy consumed from Storage by the Load (buck converter).
    @abstractmethod
    def calculate_energy_consumed_from_storage(self, e_load: float, v_storage: float) -> float:
        pass

    # Refreshes the PMIC's state at each time step t.
    #   e_supply  — energy available from the Supply at t
    #   e_load    — energy consumed by the Load at t
    #   v_storage — storage voltage at (t-1)
    @abstractmethod
    def refresh(self, e_supply: float, e_load: float, v_storage: float, t_step: float) -> None:
        self.vbat_ok = self.update_vbat_ok_signal(v_storage)
        self.v_out = self.calculate_v_out(v_storage)
        self.energy_to_storage = self.calculate_energy_supplied_to_storage(
            e_supply, v_storage)
        self.energy_from_storage = self.calculate_energy_consumed_from_storage(
            e_load, v_storage)

    @abstractmethod
    def print(self, t_index: int, file) -> None:
        print(
            f"PMIC: {self.type} --> "
            f"t={t_index},"
            f"status={self.status},"
            f"v_out={self.v_out:.5f}V,"
            f"vbat_ok={self.vbat_ok},"
            f"energy_to_storage={self.energy_to_storage:.5f}J,"
            f"energy_from_storage={self.energy_from_storage:.5f}J",
            file=file
        )


# Class BoostBuckPMIC for the BEHS simulation model, inheriting from PMIC Class
# Represents a PMIC with a boost charger and a buck converter.
class BoostBuckPMIC(PMIC):
    def __init__(self, config):
        self.V_IN_COLD_START = config.get("v_in_cold_start")
        self.V_BOOST_THRESH = config.get("v_boost_thresh")
        self.V_BAT_UV = config.get("v_bat_uv")
        self.V_BAT_OV = config.get("v_bat_ov")
        self.V_BAT_OK_LOW = config.get("v_bat_ok_low")
        self.V_BAT_OK_HIGH = config.get("v_bat_ok_high")
        self.V_OUT_REG = config.get("v_out_reg")

        self.type = config.get("type")
        self.consider_efficiency = config.get("consider_efficiency", True)
        self.status = "off"
        self.v_out = 0.0
        self.vbat_ok = False
        self.energy_to_storage = 0.0
        self.energy_from_storage = 0.0

        if self.consider_efficiency:
            self.MPPT_EFFICIENCY = config.get("mppt_efficiency")
            self.BOOST_EFFICIENCY = config.get("boost_efficiency")
            self.BUCK_EFFICIENCY = config.get("buck_efficiency")
            self.COLD_START_EFFICIENCY = config.get("cold_start_efficiency")

    # Updates the VBAT_OK flag, which is used to turn on the buck converter (enable v_on to Load).
    # - It goes False --> True when v_storage >= V_BAT_OK_HIGH.
    # - It stays True while v_storage >= V_BAT_OK_LOW.
    # - It goes True --> False when v_storage < V_BAT_OK_LOW.
    def update_vbat_ok_signal(self, v_storage):
        if self.vbat_ok:
            return v_storage >= self.V_BAT_OK_LOW
        else:
            return v_storage >= self.V_BAT_OK_HIGH

    # Calculates the output voltage delivered to the load.
    # - Disabled: v_out = 0.0V when vbat_ok is False or v_storage <= V_BAT_UV.
    # - Pass-through (100% duty cycle): v_out = v_storage, when V_BAT_UV < v_storage < V_OUT_REG.
    # - Regulated: v_out = V_OUT_REG, when v_storage >= V_OUT_REG.
    def calculate_v_out(self, v_storage):
        if not self.vbat_ok or v_storage <= self.V_BAT_UV:
            return 0.0
        if v_storage < self.V_OUT_REG:
            return v_storage
        return self.V_OUT_REG

    # Energy charged into storage by supply per time step:
    # - e_to_storage = e_supply * n_mppt * n_boost, when storage is in "boost_only" mode.
    # - e_to_storage = e_supply * n_cold_start, when storage is on "cold_start" mode.
    def calculate_energy_supplied_to_storage(self, e_supply, v_storage):
        if e_supply <= 0.0 or v_storage >= self.V_BAT_OV:
            return 0.0
        if v_storage < self.V_BOOST_THRESH:
            return e_supply * self.COLD_START_EFFICIENCY
        return e_supply * self.MPPT_EFFICIENCY * self.BOOST_EFFICIENCY

    # Energy consumed from storage by load on each time step:
    #   e_from_storage = e_load / n_buck
    # Buck is disabled when vbat_ok is False or v_storage <= V_BAT_UV.
    def calculate_energy_consumed_from_storage(self, e_load, v_storage):
        if e_load <= 0.0 or not self.vbat_ok or v_storage <= self.V_BAT_UV:
            return 0.0
        return e_load / self.BUCK_EFFICIENCY

    # Refreshes the PMIC's state at each time step t.
    # - "cold_start" mode is when v_storage < V_BOOST_THRESH.
    # - "boost_only" mode is when V_BOOST_THRESH <= v_storage < V_BAT_UV.
    # - "charging" mode is when energy is being transferred into storage (supply > load).
    # - "discharging" mode is when energy is being drawn from storage (supply < load).
    # - "idle" mode is when energy supply and energy consumption are equal.
    # - "full" mode is when storage voltage is at maximum, >= V_BAT_OV.
    def refresh(self, e_supply: float, e_load: float, v_storage: float, t_step: float) -> None:
        super().refresh(e_supply, e_load, v_storage, t_step)

        if v_storage < self.V_BOOST_THRESH:
            self.status = "cold_start"
        elif v_storage < self.V_BAT_UV:
            self.status = "boost_only"
        elif v_storage >= self.V_BAT_OV:
            self.status = "full"
        elif self.energy_to_storage > self.energy_from_storage:
            self.status = "charging"
        elif self.energy_from_storage > self.energy_to_storage:
            self.status = "discharging"
        else:
            self.status = "idle"

    def print(self, t_index, file):
        super().print(t_index, file)
