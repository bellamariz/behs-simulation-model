from __future__ import annotations
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.interface.interface import Interface

# A program instruction (Operation) is processed every PROCESSING_CLOCK.
DEFAULT_PROCESSING_CLOCK = 0.001
# NOTE: If PROCESSING_CLOCK  is larger than the simulation time step, it will cause inaccuracies.
# Therefore, the simulator assumes PROCESSING_CLOCK is always <= than the time step and greater than default 1ms.

# There are two models for calculating the Operation cost per PROCESSING_CLOCK tick.

# 1) FLOAT MODEL (sub-tick): Operation duration is as is
# Within each PROCESSING_CLOCK tick,
#   - an operation i may end before the tick ends (if duration < PROCESSING_CLOCK);
#   - the next operation i+1 will begin in the same tick
# The cost of each operation is proportional to the fraction of the tick it occupies:
#   - Task Cost = op.cost * (elapsed / duration)
#   - Base CPU Cost = cpu_cost * (elapsed / t_step)
# Tracks duration and cost accurately, regardless of PROCESSING_CLOCK value (as long as PROCESSING_CLOCK <= t_step).
# Will have precision issues if PROCESSING_CLOCK is not a multiple of t_step.
CLOCK_TICK_MODEL_FLOAT = "float"

# 2) INTEGER MODEL (full-tick): if Operation duration < PROCESSING_CLOCK, it occupies at least one tick
# Within each PROCESSING_CLOCK tick,
#   - all operations occupy at least one full tick (no partial ticks, even if their duration < PROCESSING_CLOCK);
#   - the next operation i+1 only starts in the next tick.
# The cost of each operation is proportional to the tick it occupies:
#   - Task Cost = op.cost / ticks_needed per tick.
#   - Base CPU Cost = cpu_cost / ticks_per_t_step per tick.
# Only tracks duration and cost accurately for smaller PROCESSING_CLOCK values, e.g. 1ms (as long as PROCESSING_CLOCK <= t_step).
# Will have precision issues if PROCESSING_CLOCK is not a multiple of t_step.
CLOCK_TICK_MODEL_INTEGER = "integer"


# Class Operation for the BEHS simulation model
# It represents one software operation executed by a MCU Load
class Operation:
    def __init__(self, name: str, instruction: str):
        self.name = name
        self.instruction = instruction
        self.cost = 0.0  # consumption current cost (in Amp)
        self.duration = 0.0  # duration (in milliseconds)
        self.ticks_needed = 0  # duration (in PROCESSING_CLOCK ticks)


# Default Operation registry
# - The PROC operation is a CPU operation in the "active" mode
# - The SLEEP operation is a CPU operation in the "standby" mode
# - The remaining operations have a fixed cost, which will be summed to the CPU mode base cost ("standby" or "active")
_OPERATION_REGISTRY = {
    "PROC": Operation(name="cpu_processing", instruction="PROC"),
    "SLEEP": Operation(name="cpu_sleeping", instruction="SLEEP"),
    "SENSE": Operation(name="sensing", instruction="SENSE"),
    "TX": Operation(name="transmitting", instruction="TX"),
    "RX": Operation(name="receiving", instruction="RX"),
    "CHECKPOINT": Operation(name="checkpointing", instruction="CHECKPOINT"),
    "TASK": Operation(name="task_block", instruction="TASK"),
}


# Class Program represents a script of code that will be executed by the MCU Load
# It reads the program file and loads the operations and their duration
# Execution advances each PROCESSING_CLOCK, allowing multiple operations per simulation time step.
class Program:
    def __init__(self, filepath: str, interface: "Interface", cpu_active_cost: float, cpu_standby_cost: float,
                 cpu_shutdown_cost: float, processing_clock: float, tick_model: str = CLOCK_TICK_MODEL_FLOAT):

        self.FILEPATH = filepath
        self.CPU_ACTIVE_COST = cpu_active_cost
        self.CPU_STANDBY_COST = cpu_standby_cost
        self.CPU_SHUTDOWN_COST = cpu_shutdown_cost
        self.TICK_MODEL = tick_model
        self.PROCESSING_CLOCK = processing_clock

        operations = self._parse_program_file(filepath)
        self.operations = self._parse_operations(operations)
        self.interface = interface

        # Tracks elapsed seconds per instruction during the last t_step
        # Format: {instruction: elapsed_seconds}
        self.executed_ops_last_step: dict[str, float] = {}

        # Control execution state:
        #   - index of the currently executing operation
        #   - how many PROCESSING_CLOCK ticks are left to finish executing it
        self.current_op_index = 0
        self.current_op_remaining_ticks = 0           # integer model: ticks left
        self.current_op_remaining_seconds = 0.0       # float model: seconds left
        self.get_next_valid_op()  # Initialize the first valid operation to execute

    # Print Program object
    def print(self):
        print(f"=== Program to be executed: {self.FILEPATH} ===")
        print(
            f"processing_clock={self.PROCESSING_CLOCK}, tick_model={self.TICK_MODEL}, interface={self.interface.name}, program_model={self.interface.program_execution_model}")
        print("operations=")
        self.print_operations()

    # Print operations list of the Program object
    def print_operations(self):
        for i, op in enumerate(self.operations):
            print(
                f"  #{i} | name={op.name}, inst={op.instruction}, cost={op.cost:.6f}A, duration={op.duration*1000:.2f}ms, ticks={op.ticks_needed}")

    # Reset program execution if program does not save state and Load loses power
    def reset(self):
        self.interface.program_reset(self)

    # Get next valid operation to execute
    def get_next_valid_op(self):
        self.interface.program_get_next_valid_op(self)

    # Processes the execution cost of the Program for a given time step, t_step.
    # Goes through all the operations that fit (even partially) within t_step.
    # For each tick (PROCESSING_CLOCK), it computes:
    #   - the CPU mode cost (standby or active);
    #   - the operation cost;
    # Starts Program again if all operations are exhausted before t_step is complete.
    def get_cost_for_t_step(self, t_step: float, v_supply: float) -> float:
        if self.TICK_MODEL == CLOCK_TICK_MODEL_INTEGER:
            return self.interface.program_get_cost_integer(t_step, v_supply, self)
        return self.interface.program_get_cost_float(t_step, v_supply, self)

    # Returns True if the Program has a CHECKPOINT operation.
    # It allows saving state and resuming execution after a power loss.
    def has_checkpoint(self) -> bool:
        return any(op.instruction == "CHECKPOINT" for op in self.operations)

    # Read program file, skipping comment lines
    def _parse_program_file(self, filepath: str) -> list[str]:
        lines = []
        with open(filepath, 'r') as file:
            for line in file:
                # Get line
                l = line.strip()

                # Skip comments and blank lines
                if l == "" or l.startswith("#"):
                    continue

                # Append line to list of operations otherwise
                lines.append(l)

        return lines

    # Parse the program file and create a list of Operation objects
    def _parse_operations(self, operations_from_file: list[str]) -> list[Operation]:
        operations = []
        for op in operations_from_file:
            # Parse operation line: 'INSTRUCTION [COST] [DURATION]'
            parts = op.split()
            if len(parts) > 3:
                print(
                    f"Warning: Operation '{op}' format is not recognized. Skipping.")
                continue

            # Validate instruction
            instruction = parts[0]
            if instruction not in _OPERATION_REGISTRY:
                print(
                    f"Warning: Instruction '{instruction}' is not recognized. Skipping.")
                continue

            # Validate cost
            cost = float(parts[1]) if len(parts) >= 2 else 0.0

            # Validate duration
            duration = float(parts[2]) if len(parts) == 3 else 0.0
            duration_in_seconds = duration / 1000.0

            # Build new Operation object (copy to avoid mutating registry)
            registry_op = _OPERATION_REGISTRY[instruction]
            new_op = Operation(
                name=registry_op.name,
                instruction=registry_op.instruction,
            )
            new_op.cost = cost
            new_op.duration = duration_in_seconds

            # Get PROCESSING_CLOCK ticks needed to execute based on duration
            if duration_in_seconds > 0:
                new_op.ticks_needed = math.ceil(
                    duration_in_seconds / self.PROCESSING_CLOCK)

            # Append Operation object to the list
            operations.append(new_op)

        return operations
