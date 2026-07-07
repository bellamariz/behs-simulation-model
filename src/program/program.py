import math

# A program instruction (Operation) is processed every PROCESSING_CLOCK.
DEFAULT_PROCESSING_CLOCK = 0.001
# NOTE: If PROCESSING_CLOCK  is larger than the simulation time step, it will cause inaccuracies.
# Therefore, the simulator assumes PROCESSING_CLOCK is always <= than the time step.

# There two models for calculating the Operation cost per PROCESSING_CLOCK tick:
# 1) sub-tick: Operation duration is as is
CLOCK_TICK_MODEL_FLOAT = "float"
# 2) full-tick: if Operation duration < PROCESSING_CLOCK, it occupies at least one tick
CLOCK_TICK_MODEL_INTEGER = "integer"


# Class Operation for the BEHS simulation model
# It represents one software operation executed by a MCU Load
class Operation:
    def __init__(self, name: str, instruction: str):
        self.name = name
        self.instruction = instruction
        self.cost = 0.0  # consumption current cost (for given duration)
        self.duration = 0.0  # duration in seconds
        self.ticks_needed = 0  # duration parsed to PROCESSING_CLOCK ticks
        self.unknown_duration = False  # True if duration is unknown


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
}


# Class Program represents a script of code that will be executed by the MCU Load
# It reads the program file and loads the operations and their duration
# Execution advances each PROCESSING_CLOCK, allowing multiple operations per simulation time step.
class Program:
    def __init__(self, filepath: str, cpu_active_cost: float, cpu_standby_cost: float,
                 tick_model: str = CLOCK_TICK_MODEL_FLOAT, processing_clock: float = DEFAULT_PROCESSING_CLOCK):

        self.FILEPATH = filepath
        self.CPU_ACTIVE_COST = cpu_active_cost
        self.CPU_STANDBY_COST = cpu_standby_cost
        self.TICK_MODEL = tick_model
        self.PROCESSING_CLOCK = processing_clock

        operations_from_file = self._parse_program_file(filepath)
        self.operations = self._parse_operations(operations_from_file)

        # Control execution state:
        #   - index of the currently executing operation
        #   - how many PROCESSING_CLOCK ticks are left to finish executing it
        self.current_op_index = 0
        self.current_op_remaining_ticks = 0           # integer model: ticks left
        self.current_op_remaining_seconds = 0.0       # float model: seconds left
        self._advance_to_next_valid_op()

    # Processes one simulation time step and gets the total cost for it.
    # For each tick (PROCESSING_CLOCK), it computes:
    #   - the CPU mode cost (standby or active);
    #   - the operation cost;
    # Goes through all the operations that fit (even partially) within this t_step.
    # Starts program again if all operations are exhausted before t_step is complete.
    def get_cost_for_t_step(self, t_step: float) -> float:
        if self.TICK_MODEL == CLOCK_TICK_MODEL_FLOAT:
            return self._get_cost_float(t_step)
        return self._get_cost_integer(t_step)

    # FLOAT MODEL
    # Within each PROCESSING_CLOCK tick, an operation may end before tick ends
    # The next Operation may begin in the same tick
    # - Task Cost = op.cost * (elapsed / duration)
    # - Base CPU Cost = cpu_cost * (elapsed / t_step)
    #
    # More accurate results regardless of PROCESSING_CLOCK (if <= t_step),
    # but elapsed time tracking may have precision issues since it handles very small floats.
    def _get_cost_float(self, t_step: float) -> float:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(1, math.ceil(t_step / self.PROCESSING_CLOCK))
        estimated_zero = 1e-12

        total_cost = 0.0
        for _ in range(ticks_per_t_step):
            remaining_tick = self.PROCESSING_CLOCK

            # Finish inner loop when tick is complete or when there are no operations left
            # NOTE: When tracking the elapsed time of an Operation within a tick, we may encounter precision issues with very small floats
            # Instead of checking for remaining_tick > 0, we check for a small value close to 0
            while remaining_tick > estimated_zero:
                # If program is finished, start again from the beginning
                # TODO: Also start over if MCU is no longer in active mode - depends on interface
                if self.current_op_index >= len(self.operations):
                    # Reset current_op_index and get next valid operation
                    self.current_op_index = 0
                    self._get_next_valid_op()

                    # Abort execution if the program has no valid operations
                    if self.current_op_index >= len(self.operations):
                        break

                # Get the current operation and its elapsed time for this tick
                op = self.operations[self.current_op_index]
                elapsed = min(remaining_tick,
                              self.current_op_remaining_seconds)

                # Calculate operation cost for the elapsed time
                if op.duration >= t_step:
                    total_cost += op.cost * (elapsed / t_step)
                else:
                    total_cost += op.cost * (elapsed / op.duration)

                # Add active CPU cost for non-CPU instructions
                if op.instruction not in ["SLEEP", "PROC"]:
                    total_cost += self.CPU_ACTIVE_COST * (elapsed / t_step)

                # Decrease the remaining seconds necessary to complete operation
                self.current_op_remaining_seconds -= elapsed
                remaining_tick -= elapsed

                # Move to next operation once current one is over
                # NOTE: Since we are possibly dealing with very small floats, precision is an issue
                # Instead of checking for remaining_seconds <= 0, we check for a small value close to 0
                if self.current_op_remaining_seconds <= estimated_zero:
                    self.current_op_index += 1
                    self._get_next_valid_op()

        return total_cost

    # INTEGER MODEL
    # Each Operation occupies a whole number of ticks (at least one, if its duration < PROCESSING_CLOCK)
    # The next Operation only starts in the next tick
    #   - Task Cost = op.cost / ticks_needed per tick.
    #   - Base CPU Cost = cpu_cost / ticks_per_t_step per tick.
    #
    # More accurate results for smaller PROCESSING_CLOCK values (e.g. 1ms),
    # but elapsed time tracking is more solid and well-defined since it uses integer ticks.
    def _get_cost_integer(self, t_step: float) -> float:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(1, math.ceil(t_step / self.PROCESSING_CLOCK))

        total_cost = 0.0
        for _ in range(ticks_per_t_step):
            # If program is finished, start again from the beginning
            # TODO: Also start over if MCU is no longer in active mode - depends on interface
            if self.current_op_index >= len(self.operations):
                # Reset current_op_index and get next valid operation
                self.current_op_index = 0
                self._get_next_valid_op()

                # Abort execution if the program has no valid operations
                if self.current_op_index >= len(self.operations):
                    break

            # Get the current operation for this tick
            op = self.operations[self.current_op_index]

            # Calculate total cost for this tick
            if op.duration >= t_step:
                total_cost += op.cost / ticks_per_t_step
            else:
                total_cost += op.cost / op.ticks_needed

            # Add active CPU cost for non-CPU instructions
            if op.instruction not in ["SLEEP", "PROC"]:
                total_cost += self.CPU_ACTIVE_COST / ticks_per_t_step

            # Decrease the remaining ticks necessary to complete operation
            self.current_op_remaining_ticks -= 1

            # Advance to next operation once there are no ticks left for operation
            if self.current_op_remaining_ticks <= 0:
                self.current_op_index += 1
                self._get_next_valid_op()

        return total_cost

    # Makes current_op_index skip operations with zero duration
    # Defines current_op_remaining_time (seconds/ticks) for the next valid operation
    def _get_next_valid_op(self):
        while self.current_op_index < len(self.operations):
            # Get the next operation that needs to be executed
            op = self.operations[self.current_op_index]

            # Skip operation if their duration is unknown
            # Otherwise, set how much time (seconds or ticks) is needed to execute it
            if op.unknown_duration:
                # TODO: Handle operations with unknown duration
                self.current_op_index += 1
            else:
                self.current_op_remaining_seconds = op.duration
                self.current_op_remaining_ticks = op.ticks_needed

    # Print Operations list of the Program object
    def print_operations(self):
        for i, op in enumerate(self.operations):
            print(
                f"  #{i} | name={op.name}, inst={op.instruction}, cost={op.cost:.6f}, duration={op.duration:.6f}, ticks={op.ticks_needed}, unknown_duration={op.unknown_duration}")

    # Print Program attributes
    def print(self):
        print(f"=== Program to be executed: {self.FILEPATH} ===")
        print("operations=")
        self.print_operations()

    # Read program file
    def _parse_program_file(self, filepath: str) -> list[str]:
        with open(filepath, 'r') as file:
            return [line.strip() for line in file if line.strip()]

    # Parse the program file and create a list of Operation objects
    def _parse_operations(self, operations_from_file: list[str]) -> list[Operation]:
        operations = []
        for op in operations_from_file:
            # Parse operation line: 'INSTRUCTION COST [DURATION]'
            parts = op.split()
            if len(parts) not in [2, 3]:
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

            # Build new Operation object (copy to avoid mutating registry)
            registry_op = _OPERATION_REGISTRY[instruction]
            new_op = Operation(
                name=registry_op.name,
                instruction=registry_op.instruction,
            )
            new_op.cost = cost
            new_op.duration = duration

            # Get PROCESSING_CLOCK ticks needed to execute based on duration
            # TODO: Process instructions of unknown duration
            if duration > 0:
                new_op.ticks_needed = math.ceil(
                    duration / self.PROCESSING_CLOCK)
            else:
                new_op.unknown_duration = True

            # Append Operation object to the list
            operations.append(new_op)

        return operations
