from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.program.program import Program


class Interface(ABC):
    @abstractmethod
    def __init__(self):
        self.name: str
        self.program_model: str

    @abstractmethod
    def program_get_cost_float(self, t_step: float, program: "Program") -> float:
        pass

    @abstractmethod
    def program_get_cost_integer(self, t_step: float, program: "Program") -> int:
        pass

    @abstractmethod
    def program_get_next_valid_op(self, program: "Program"):
        pass

    @abstractmethod
    def program_reset(self, program: "Program"):
        pass


class Basic(Interface):
    def __init__(self):
        self.name = "Basic"
        self.program_model = "NONE"

    def program_get_cost_float(self, t_step: float, prog: "Program") -> float:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(
            1, round(t_step / prog.PROCESSING_CLOCK))
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
                # TODO: Also start over if MCU is no longer in active mode - depends on interface
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

    def program_get_cost_integer(self, t_step: float, prog: "Program") -> int:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(1, round(t_step / prog.PROCESSING_CLOCK))
        prog.executed_ops_last_step = {}

        total_cost = 0.0
        for _ in range(ticks_per_t_step):
            # If program is finished, start again from the beginning
            # TODO: Also start over if MCU is no longer in active mode - depends on interface
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

    def program_get_next_valid_op(self, prog: "Program"):
        while prog.current_op_index < len(prog.operations):
            # Get the next operation that needs to be executed
            op = prog.operations[prog.current_op_index]

            # Skip operation if their duration is unknown
            # Otherwise, set how much time (seconds or ticks) is needed to execute it
            if op.duration <= 0.0:
                # TODO: Handle operations with unknown duration
                prog.current_op_index += 1
            else:
                prog.current_op_remaining_seconds = op.duration
                prog.current_op_remaining_ticks = op.ticks_needed
                return

    def program_reset(self, prog: "Program"):
        prog.current_op_index = 0
        prog.current_op_remaining_ticks = 0
        prog.current_op_remaining_seconds = 0.0
        prog.executed_ops_last_step = {}
        prog.get_next_valid_op()


class Hibernus(Interface):
    def __init__(self):
        self.name = "Hibernus"
        self.program_model = "CHECKPOINTING"

    def program_get_cost_float(self, t_step: float, program: "Program") -> float:
        pass

    def program_get_cost_integer(self, t_step: float, program: "Program") -> int:
        pass

    def program_get_next_valid_op(self, program: "Program"):
        pass


class UFoP(Interface):
    def __init__(self):
        self.name = "UFoP"
        self.program_model = "TASK-BASED"

    def program_get_cost_float(self, t_step: float, program: "Program") -> float:
        pass

    def program_get_cost_integer(self, t_step: float, program: "Program") -> int:
        pass

    def program_get_next_valid_op(self, program: "Program"):
        pass
