# Class Operation for the BEHS simulation model
# It represents one software operation executed by a MCU Load
# We assume only ONE Operation is executed per simulation time step.
class Operation:
    def __init__(self, name: str, instruction: str, cost: float):
        self.name = name
        self.instruction = instruction
        self.cost = cost
        self.duration = 0.0
        self.t_steps_needed = 0

    # Calculates the operation cost for a given simulation time step
    def get_cost_for_t_step(self, t_step: float) -> float:
        if self.duration < t_step:
            return self.cost * (self.duration / t_step)
        else:
            return self.cost

    # Calculates the number of simulation time steps needed to complete the operation
    def get_t_steps_needed(self, t_step: float) -> int:
        if self.duration == 0.0:
            return 0

        # Value is rounded to the nearest integer
        steps = round(self.duration / t_step)

        # If result is too small, Python will round it to 0
        # But we assume each Operation takes at least 1 simulation time step
        if steps <= 0:
            return 1

        return steps


# Default Operation registry
# - The STANDBY and ACTION are CPU operations and get their cost from Load class
# - The LOOP and END operations have zero cost and duration
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
# We assume only ONE Operation is executed per simulation time step.
class Program:
    def __init__(self, t_step: float, filepath: str, cpu_active_cost: float, cpu_standby_cost: float):
        operations_from_file = self._parse_program_file(filepath)

        self.FILEPATH = filepath
        self.CPU_ACTIVE_COST = cpu_active_cost
        self.CPU_STANDBY_COST = cpu_standby_cost

        self.operations = self._parse_operations(operations_from_file, t_step)
        self.t_steps_needed = sum(op.t_steps_needed for op in self.operations)
        self.t_steps_completed = 0

    # Returns the executing Operation for current time step
    def get_executing_operation(self) -> 'Operation':
        if self.t_steps_needed == 0:
            return None

        # Get the index of the current time step in the program execution
        index = self.t_steps_completed % self.t_steps_needed

        # Search through Operations list to find the one currently executing
        steps = 0
        for op in self.operations:
            if op.t_steps_needed == 0:
                continue

            steps += op.t_steps_needed
            if index < steps:
                return op

        return None

    # Print Operations list of the Program object
    def print_operations(self):
        for i, op in enumerate(self.operations):
            print(
                f"  #{i} | name={op.name}, inst={op.instruction}, dur={op.duration:.5f}, cost={op.cost:.5f}, steps={op.t_steps_needed}")

    # Print Program attributes
    def print(self):
        print(f"=== Executed Program: {self.FILEPATH} ===")
        print(f"t_steps_needed={self.t_steps_needed},")
        print("operations=")
        self.print_operations()

    # Read program file
    def _parse_program_file(self, filepath: str) -> list[str]:
        with open(filepath, 'r') as file:
            return [line.strip() for line in file if line.strip()]

    def _parse_operations(self, operations_from_file: list[str], t_step: float) -> list[Operation]:
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
            new_op.duration = duration

            # Number of simulation steps needed to complete the operation
            # Value is rounded to the nearest integer
            new_op.t_steps_needed = new_op.get_t_steps_needed(t_step)

            if instruction == "ACTIVE":
                new_op.cost = self.CPU_ACTIVE_COST
            elif instruction == "STANDBY":
                new_op.cost = self.CPU_STANDBY_COST

            # Append Operation object to the list
            operations.append(new_op)

        return operations
