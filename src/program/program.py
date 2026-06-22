# Class Operation for the BEHS simulation model
# It represents one software operation executed by a MCU Load.
class Operation:
    def __init__(self, name: str, instruction: str, cost: float):
        self.name = name
        self.instruction = instruction
        self.cost = cost


# Default Operation registry
# The STANDBY and ACTION operations do not have their final cost yet.
_OPERATION_REGISTRY = {
    "STANDBY": Operation(name="cpu_standby", instruction="STANDBY", cost=0.0),
    "ACTIVE": Operation(name="cpu_processing", instruction="ACTIVE", cost=0.0),
    "SENSE": Operation(name="sensing", instruction="SENSE", cost=0.006),
    "TX": Operation(name="transmitting", instruction="TX", cost=0.03),
    "RX": Operation(name="receiving", instruction="RX", cost=0.027),
}


# Class Program represents a script of code that will be executed by the MCU Load
# It reads the program file and loads the operations and their duration.
class Program:
    def __init__(self, filepath: str, mcu_active_cost: float, mcu_standby_cost: float):
        operations_from_file = self._read_program_file(filepath)
        self.filepath = filepath
        self.operations = self._parse_operations(
            operations_from_file, mcu_active_cost, mcu_standby_cost)

    # Read program file
    def _read_program_file(self, filepath: str) -> list[str]:
        with open(filepath, 'r') as file:
            return [line.strip() for line in file if line.strip()]

    def _parse_operations(self, operations_from_file: list[str], mcu_active_cost: float, mcu_standby_cost: float) -> list[Operation]:
        operations = []
        for op in operations_from_file:
            # Ignore operations that do not have duration
            parts = op.split()
            if len(parts) != 2:
                continue

            # Parse instruction and duration
            instruction = parts[0]
            duration = float(parts[1])
            if instruction not in _OPERATION_REGISTRY:
                print(
                    f"Warning: Instruction '{instruction}' is not recognized. Skipping.")
                continue

            # Get operation from registry
            new_op = _OPERATION_REGISTRY[instruction]
            if instruction == "ACTIVE":
                new_op.cost = mcu_active_cost
            elif instruction == "STANDBY":
                new_op.cost = mcu_standby_cost

            # Append operation to the list
            operations.append(new_op)

        return operations
