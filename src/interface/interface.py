from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.program.program import Program


class Interface(ABC):
    @abstractmethod
    def __init__(self):
        self.name: str
        self.energy_monitoring_device: str
        self.energy_monitoring_strategy: str
        self.program_execution_model: str
        self.program_saves_state: bool

    @abstractmethod
    def program_get_cost_float(self, t_step: float, v_supply: float, prog: "Program") -> float:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(1, round(t_step / prog.PROCESSING_CLOCK))
        estimated_zero = 1e-12
        prog.executed_ops_last_step = {}

        total_cost = 0.0
        for _ in range(ticks_per_t_step):
            remaining_tick = prog.PROCESSING_CLOCK

            # Finish inner loop when tick is complete or when there are no operations left
            # NOTE: When tracking the elapsed time of an Operation within a tick, we may encounter precision issues with very small floats
            # Instead of checking for remaining_tick > 0, we check for a small value close to 0
            while remaining_tick > estimated_zero:
                # If program is finished, start again from the beginning
                if prog.current_op_index >= len(prog.operations):
                    # Reset current_op_index and get next valid operation
                    prog.current_op_index = 0
                    prog.get_next_valid_op()

                    # Abort execution if the program has no valid operations
                    if prog.current_op_index >= len(prog.operations):
                        break

                # Get the current operation and its elapsed time for this tick
                op = prog.operations[prog.current_op_index]
                elapsed = min(remaining_tick,
                              prog.current_op_remaining_seconds)

                # Track elapsed seconds per instruction for this t_step
                instruct = op.instruction
                prog.executed_ops_last_step[instruct] = prog.executed_ops_last_step.get(
                    instruct, 0.0) + elapsed

                # Calculate operation cost for the elapsed time
                if op.duration >= t_step:
                    total_cost += op.cost * (elapsed / t_step)
                else:
                    total_cost += op.cost * (elapsed / op.duration)

                # Add active CPU cost for non-CPU instructions
                if op.instruction not in ["SLEEP", "PROC"]:
                    total_cost += prog.CPU_ACTIVE_COST * (elapsed / t_step)

                # Decrease the remaining seconds necessary to complete operation
                prog.current_op_remaining_seconds -= elapsed
                remaining_tick -= elapsed

                # Move to next operation once current one is over
                # NOTE: Since we are possibly dealing with very small floats, precision is an issue
                # Instead of checking for remaining_seconds <= 0, we check for a small value close to 0
                if prog.current_op_remaining_seconds <= estimated_zero:
                    prog.current_op_index += 1
                    prog.get_next_valid_op()

        return total_cost

    @abstractmethod
    def program_get_cost_integer(self, t_step: float, v_supply: float, prog: "Program") -> int:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(1, round(t_step / prog.PROCESSING_CLOCK))
        prog.executed_ops_last_step = {}

        total_cost = 0.0
        for _ in range(ticks_per_t_step):
            # If program is finished, start again from the beginning
            if prog.current_op_index >= len(prog.operations):
                # Reset current_op_index and get next valid operation
                prog.current_op_index = 0
                prog.get_next_valid_op()

                # Abort execution if the program has no valid operations
                if prog.current_op_index >= len(prog.operations):
                    break

            # Get the current operation for this tick
            op = prog.operations[prog.current_op_index]

            # Track elapsed seconds per instruction for this t_step
            instruct = op.instruction
            prog.executed_ops_last_step[instruct] = prog.executed_ops_last_step.get(
                instruct, 0.0) + prog.PROCESSING_CLOCK

            # Calculate total cost for this tick
            if op.duration >= t_step:
                total_cost += op.cost / ticks_per_t_step
            else:
                total_cost += op.cost / op.ticks_needed

            # Add active CPU cost for non-CPU instructions
            if op.instruction not in ["SLEEP", "PROC"]:
                total_cost += prog.CPU_ACTIVE_COST / ticks_per_t_step

            # Decrease the remaining ticks necessary to complete operation
            prog.current_op_remaining_ticks -= 1

            # Advance to next operation once there are no ticks left for operation
            if prog.current_op_remaining_ticks <= 0:
                prog.current_op_index += 1
                prog.get_next_valid_op()

        return total_cost

    @abstractmethod
    def program_get_next_valid_op(self, prog: "Program"):
        while prog.current_op_index < len(prog.operations):
            # Get the next operation that needs to be executed
            op = prog.operations[prog.current_op_index]

            # Skip operation if their duration is unknown (e.g. CHECKPOINT is just a marker)
            # Otherwise, set how much time (seconds or ticks) is needed to execute it
            if op.duration <= 0.0:
                prog.current_op_index += 1
            else:
                prog.current_op_remaining_seconds = op.duration
                prog.current_op_remaining_ticks = op.ticks_needed
                return

    @abstractmethod
    def program_reset(self, prog: "Program"):
        if self.program_saves_state:
            return

        prog.current_op_index = 0
        prog.current_op_remaining_ticks = 0
        prog.current_op_remaining_seconds = 0.0
        prog.executed_ops_last_step = {}
        prog.get_next_valid_op()

    @abstractmethod
    def program_manage_execution(self, v_supply: float, t_step: float, prog: "Program",
                                 load_mode_last: str, load_mode_from_supply: str) -> tuple[str, float]:
        cost = 0.0
        if load_mode_from_supply == "active":
            cost = prog.get_cost_for_t_step(t_step, v_supply)
        else:
            prog.executed_ops_last_step = {}
            if load_mode_from_supply == "standby":
                cost = prog.CPU_STANDBY_COST
            elif load_mode_from_supply == "shutdown":
                cost = prog.CPU_SHUTDOWN_COST
        return load_mode_from_supply, cost

    @abstractmethod
    def print(self):
        print(f"Interface: {self.name}, "
              f"energy_monitoring_device={self.energy_monitoring_device}, "
              f"energy_monitoring_strategy={self.energy_monitoring_strategy}, "
              f"program_execution_model={self.program_execution_model}"
              )


class Basic(Interface):
    def __init__(self):
        self.name = "Basic"
        self.energy_monitoring_device = "NONE"
        self.energy_monitoring_strategy = "NONE"
        self.program_execution_model = "NONE"
        self.program_saves_state = False

    def program_get_cost_float(self, t_step: float, v_supply: float, prog: "Program") -> float:
        return super().program_get_cost_float(t_step, v_supply, prog)

    def program_get_cost_integer(self, t_step: float, v_supply: float, prog: "Program") -> int:
        return super().program_get_cost_integer(t_step, v_supply, prog)

    def program_get_next_valid_op(self, prog: "Program"):
        super().program_get_next_valid_op(prog)

    def program_reset(self, prog: "Program"):
        super().program_reset(prog)

    def program_manage_execution(self, v_supply, t_step, prog, load_mode_last, load_mode_from_supply) -> tuple[str, float]:
        return super().program_manage_execution(v_supply, t_step,
                                                prog, load_mode_last, load_mode_from_supply)

    def print(self):
        super().print()


class Mementos(Interface):
    def __init__(self):
        self.name = "Mementos"
        self.energy_monitoring_device = "INTERNAL"
        self.energy_monitoring_strategy = "ACTIVE"
        self.program_execution_model = "CHECKPOINTING"
        self.program_saves_state = True

        # NOTE: values based on the TI MSP430FR59xx MCU specs
        self.INTERNAL_ADC_COST_ACTIVE = 0.000245
        self.INTERNAL_ADC_COST_STANDBY = 0.000165
        self.FRAM_COST_ACTIVE = 0.002265  # 50% cache hit
        self.FRAM_COST_STANDBY = 0.001070
        self.V_THRESHOLD = 3.1

        # Verify if the Program started to execute a CHECKPOINT instruction
        self._execute_checkpoint = False
        self._is_snapshot_saved = False

    def program_get_cost_float(self, t_step: float, v_supply: float, prog: "Program") -> float:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(1, round(t_step / prog.PROCESSING_CLOCK))
        estimated_zero = 1e-12
        prog.executed_ops_last_step = {}

        total_cost = 0.0
        for _ in range(ticks_per_t_step):
            remaining_tick = prog.PROCESSING_CLOCK

            # Finish inner loop when tick is complete or when there are no operations left
            # NOTE: When tracking the elapsed time of an Operation within a tick, we may encounter precision issues with very small floats
            # Instead of checking for remaining_tick > 0, we check for a small value close to 0
            while remaining_tick > estimated_zero:
                # If program is finished, start again from the beginning
                if prog.current_op_index >= len(prog.operations):
                    # Reset current_op_index and get next valid operation
                    prog.current_op_index = 0
                    prog.get_next_valid_op()

                    # Abort execution if the program has no valid operations
                    if prog.current_op_index >= len(prog.operations):
                        break

                # If next operation is a CHECKPOINT, stop execution and return the accumulated cost
                if self._execute_checkpoint:
                    return total_cost

                # Get the current operation its elapsed time for this tick
                op = prog.operations[prog.current_op_index]
                elapsed = min(remaining_tick,
                              prog.current_op_remaining_seconds)

                # Track elapsed seconds per instruction for this t_step
                instruct = op.instruction
                prog.executed_ops_last_step[instruct] = prog.executed_ops_last_step.get(
                    instruct, 0.0) + elapsed

                # Calculate operation cost for the elapsed time
                if op.duration >= t_step:
                    total_cost += op.cost * (elapsed / t_step)
                else:
                    total_cost += op.cost * (elapsed / op.duration)

                # Add active CPU cost for non-CPU instructions
                if op.instruction not in ["SLEEP", "PROC"]:
                    total_cost += prog.CPU_ACTIVE_COST * (elapsed / t_step)

                # Decrease the remaining seconds necessary to complete operation
                prog.current_op_remaining_seconds -= elapsed
                remaining_tick -= elapsed

                # Move to next operation once current one is over
                # NOTE: Since we are possibly dealing with very small floats, precision is an issue
                # Instead of checking for remaining_seconds <= 0, we check for a small value close to 0
                if prog.current_op_remaining_seconds <= estimated_zero:
                    prog.current_op_index += 1
                    prog.get_next_valid_op()

        return total_cost

    def program_get_cost_integer(self, t_step: float, v_supply: float, prog: "Program") -> int:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(1, round(t_step / prog.PROCESSING_CLOCK))
        prog.executed_ops_last_step = {}

        total_cost = 0.0
        for _ in range(ticks_per_t_step):
            # If program is finished, start again from the beginning
            if prog.current_op_index >= len(prog.operations):
                # Reset current_op_index and get next valid operation
                prog.current_op_index = 0
                prog.get_next_valid_op()

                # Abort execution if the program has no valid operations
                if prog.current_op_index >= len(prog.operations):
                    break

            # If next operation is a CHECKPOINT, stop execution and return the accumulated cost
            if self._execute_checkpoint:
                return total_cost

            # Get the current operation for this tick
            op = prog.operations[prog.current_op_index]

            # Track elapsed seconds per instruction for this t_step
            instruct = op.instruction
            prog.executed_ops_last_step[instruct] = prog.executed_ops_last_step.get(
                instruct, 0.0) + prog.PROCESSING_CLOCK

            # Calculate total cost for this tick
            if op.duration >= t_step:
                total_cost += op.cost / ticks_per_t_step
            else:
                total_cost += op.cost / op.ticks_needed

            # Add active CPU cost for non-CPU instructions
            if op.instruction not in ["SLEEP", "PROC"]:
                total_cost += prog.CPU_ACTIVE_COST / ticks_per_t_step

            # Decrease the remaining ticks necessary to complete operation
            prog.current_op_remaining_ticks -= 1

            # Advance to next operation once there are no ticks left for operation
            if prog.current_op_remaining_ticks <= 0:
                prog.current_op_index += 1
                prog.get_next_valid_op()

        return total_cost

    def program_get_next_valid_op(self, prog: "Program"):
        while prog.current_op_index < len(prog.operations):
            op = prog.operations[prog.current_op_index]
            if op.duration <= 0.0:
                if op.instruction == "CHECKPOINT":
                    self._execute_checkpoint = True
                prog.current_op_index += 1
            else:
                prog.current_op_remaining_seconds = op.duration
                prog.current_op_remaining_ticks = op.ticks_needed
                return

    def program_reset(self, prog: "Program"):
        super().program_reset(prog)

    def program_manage_execution(self, v_supply, t_step, prog, load_mode_last, load_mode_from_supply):
        if not prog.has_checkpoint():
            return super().program_manage_execution(v_supply, t_step,
                                                    prog, load_mode_last, load_mode_from_supply)

        cost = 0.0
        if load_mode_from_supply == "active":
            # Get cost for executed operations
            cost = prog.get_cost_for_t_step(t_step, v_supply)

            # If Load is in active mode and current operation is a CHECKPOINT
            if load_mode_last == "active":
                if self._execute_checkpoint:
                    # Reset the flag for executing a CHECKPOINT operation
                    self._execute_checkpoint = False

                    # Add cost of energy monitoring device (ADC) and log it
                    cost += self.INTERNAL_ADC_COST_ACTIVE
                    prog.executed_ops_last_step["ADC_POLLING"] = 0.0

                    # Validate energy levels against the V_THRESHOLD
                    if v_supply <= self.V_THRESHOLD:
                        # Save program state to FRAM
                        self._is_snapshot_saved = True
                        prog.executed_ops_last_step["SAVE_STATE"] = 0.0
                        cost += self.FRAM_COST_ACTIVE
                else:
                    # Restore program state from FRAM
                    if self._is_snapshot_saved and v_supply > self.V_THRESHOLD:
                        self._is_snapshot_saved = False
                        prog.executed_ops_last_step["RESTORE_STATE"] = 0.0
                        cost += self.FRAM_COST_ACTIVE
        else:
            prog.executed_ops_last_step = {}
            if load_mode_from_supply == "standby":
                # Get cost for standby mode
                cost = prog.CPU_STANDBY_COST
            elif load_mode_from_supply == "shutdown":
                # Get cost for shutdown mode
                cost = prog.CPU_SHUTDOWN_COST
        return load_mode_from_supply, cost

    def print(self):
        super().print()


class UFoP(Interface):
    def __init__(self):
        self.name = "UFoP"
        self.energy_monitoring_device = "INTERNAL+EXTERNAL"
        self.energy_monitoring_strategy = "ACTIVE"
        self.program_execution_model = "TASK-BASED"
        self.program_saves_state = False

    def program_get_cost_float(self, t_step: float, v_supply: float, prog: "Program") -> float:
        pass

    def program_get_cost_integer(self, t_step: float, v_supply: float, prog: "Program") -> int:
        pass

    def program_get_next_valid_op(self, prog: "Program"):
        pass

    def program_reset(self, prog: "Program"):
        pass

    def program_manage_execution(self, v_supply, t_step, prog, previous_mode, default_mode):
        pass

    def print(self):
        super().print()
