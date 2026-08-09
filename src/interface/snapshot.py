# Class Snapshot is used internally by the Interface classes to save/restore the Program state
# Normally used for Interfaces with program model "CHECKPOINTING"
class Snapshot:
    def __init__(self):
        self.curr_op_index = 0
        self.curr_op_remaining_ticks = 0
        self.curr_op_remaining_seconds = 0.0
        self.exec_ops_last_step = {}

    def save(self, index: int, remaining_ticks: int, remaining_seconds: float, exec_ops_last: dict[str, float]):
        self.curr_op_index = index
        self.curr_op_remaining_ticks = remaining_ticks
        self.curr_op_remaining_seconds = remaining_seconds
        self.exec_ops_last_step = exec_ops_last.copy()

    def restore(self):
        self.curr_op_index = 0
        self.curr_op_remaining_ticks = 0
        self.curr_op_remaining_seconds = 0.0
        self.exec_ops_last_step.clear()

# TODO: Implement Snapshot for Interfaces with program model TASK-BASED
