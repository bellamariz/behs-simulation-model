import math

# A program instruction (Operation) is processed every PROCESSING_CLOCK.
PROCESSING_CLOCK = 0.01

# NOTE: It is NOT recommended to change this PROCESSING_CLOCK value.
# If its value is larger than the simulation time step, it will cause inaccuracies.


# Class Operation for the BEHS simulation model
# It represents one software operation executed by a MCU Load
class Operation:
    def __init__(self, name: str, instruction: str, cost: float):
        self.name = name
        self.instruction = instruction
        self.cost = cost  # total cost for the full operation, regardless of duration
        self.duration = 0.0
        self.ticks_needed = 0  # duration quantized to PROCESSING_CLOCK ticks


# Default Operation registry
# - The STANDBY and ACTIVE are CPU operations and get their cost from Load class
# - The LOOP and END operations have zero cost and duration
# - The remaining operations have a fixed cost, which will be added to the CPU mode base cost ("standby" or "active")
_OPERATION_REGISTRY = {
    "LOOP": Operation(name="start_loop", instruction="LOOP", cost=0.0),
    "END": Operation(name="end_loop", instruction="END", cost=0.0),
    "STANDBY": Operation(name="cpu_standby", instruction="STANDBY", cost=0.0),
    "ACTIVE": Operation(name="cpu_processing", instruction="ACTIVE", cost=0.0),
    "SENSE": Operation(name="sensing", instruction="SENSE", cost=0.006),
    "TX": Operation(name="transmitting", instruction="TX", cost=0.03),
    "RX": Operation(name="receiving", instruction="RX", cost=0.027),
}


# Class Program represents a script of code that will be executed by the MCU Load
# It reads the program file and loads the operations and their duration
# Execution advances each PROCESSING_CLOCK, allowing multiple operations per simulation time step.
class Program:
    def __init__(self, filepath: str, cpu_active_cost: float, cpu_standby_cost: float):
        operations_from_file = self._parse_program_file(filepath)

        self.FILEPATH = filepath
        self.CPU_ACTIVE_COST = cpu_active_cost
        self.CPU_STANDBY_COST = cpu_standby_cost

        self.operations = self._parse_operations(operations_from_file)
        self.total_cost = sum(op.cost for op in self.operations)
        self.total_duration = sum(op.duration for op in self.operations)

        # Execution state: index of the currently executing operation and
        # how many PROCESSING_CLOCK ticks are left to finish executing it
        self.current_op_index = 0
        self.current_op_remaining_ticks = 0
        self._advance_to_next_valid_op()

    # Processes one simulation time step and gets the total cost for it.
    # For each tick (PROCESSING_CLOCK), it computes:
    #   - the CPU mode cost (standby or active);
    #   - the operation cost;
    # Goes through all the operations that fit (even partially) within this t_step.
    # Starts program again if all operations are exhausted before t_step is complete.
    def get_cost_for_t_step(self, t_step: float) -> float:
        # Determine how many PROCESSING_CLOCK ticks fit in this t_step
        # Safeguard: if t_step < PROCESSING_CLOCK, we still process at least one tick
        ticks_per_t_step = max(1, round(t_step / PROCESSING_CLOCK))
        total_cost = 0.0

        # For every PROCESSING_CLOCK tick
        for _ in range(ticks_per_t_step):
            # Program finished - start from the beginning again
            if self.current_op_index >= len(self.operations):
                self.current_op_index = 0
                self._advance_to_next_valid_op()

                # Cancel execution if the program has no valid operations
                if self.current_op_index >= len(self.operations):
                    break

            # Get the current operation for this tick
            op = self.operations[self.current_op_index]

            # Get the CPU base cost and the operation cost
            if op.instruction == "STANDBY":
                total_cost += self.CPU_STANDBY_COST / ticks_per_t_step
            elif op.instruction == "ACTIVE":
                total_cost += self.CPU_ACTIVE_COST / ticks_per_t_step
            else:
                # CPU base cost when active + operation specific cost
                total_cost += self.CPU_ACTIVE_COST / ticks_per_t_step
                if op.cost > 0.0:
                    total_cost += op.cost / op.ticks_needed

            # Decrease the remaining ticks necessary to complete operation
            self.current_op_remaining_ticks -= 1

            # Advance to next operation once there are no ticks left for operation
            if self.current_op_remaining_ticks <= 0:
                self.current_op_index += 1
                self._advance_to_next_valid_op()

        return total_cost

    # Makes current_op_index skip operations with zero duration (LOOP, END, etc.)
    # Sets current_op_remaining_ticks for the next valid operation
    def _advance_to_next_valid_op(self):
        while self.current_op_index < len(self.operations):
            # Get the next operation that needs to be executed
            op = self.operations[self.current_op_index]
            # Set the number of PROCESSING_CLOCK ticks needed to execute this operation
            if op.ticks_needed > 0:
                self.current_op_remaining_ticks = op.ticks_needed
                return
            # Skip operations with zero duration
            self.current_op_index += 1

    # Print Operations list of the Program object
    def print_operations(self):
        for i, op in enumerate(self.operations):
            print(
                f"  #{i} | name={op.name}, inst={op.instruction}, dur={op.duration:.5f}, cost={op.cost:.5f}, ticks={op.ticks_needed}")

    # Print Program attributes
    def print(self):
        print(f"=== Program to be executed: {self.FILEPATH} ===")
        print(f"total_duration={self.total_duration:.5f}s,")
        print(f"total_cost={self.total_cost:.5f}A,")
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
            # Parse operation line: 'INSTRUCTION [DURATION]'
            parts = op.split()
            if len(parts) != 1 and len(parts) != 2:
                print(
                    f"Warning: Operation '{op}' format is not recognized. Skipping.")
                continue

            # Validate instruction
            instruction = parts[0]
            if instruction not in _OPERATION_REGISTRY:
                print(
                    f"Warning: Instruction '{instruction}' is not recognized. Skipping.")
                continue

            # Validate duration
            duration = float(parts[1]) if len(parts) == 2 else 0.0

            # Build new Operation object (copy to avoid mutating registry)
            registry_op = _OPERATION_REGISTRY[instruction]
            new_op = Operation(
                name=registry_op.name, instruction=registry_op.instruction, cost=registry_op.cost)

            # Get total duration and PROCESSING_CLOCK ticks needed to execute
            new_op.duration = duration
            new_op.ticks_needed = math.ceil(
                duration / PROCESSING_CLOCK) if duration > 0 else 0

            if instruction == "ACTIVE":
                new_op.cost = self.CPU_ACTIVE_COST
            elif instruction == "STANDBY":
                new_op.cost = self.CPU_STANDBY_COST

            # Append Operation object to the list
            operations.append(new_op)

        return operations
