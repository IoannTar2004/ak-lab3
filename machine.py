from isa import Opcode
from machine_constants import *
import json


class DataPath:
    extern_device = None

    acc = 0

    data_reg = 0

    stack_reg = 0

    address_reg = 0

    memory_bus = None

    ei = 0

    data_bus = 0

    def __init__(self, extern_device, memory_capacity):
        self.data_memory = [0] * memory_capacity
        self.extern_device = extern_device

    def signal_latch_acc(self, sel, load=0):
        self.acc = load if sel == Signal.DIRECT_ACC_LOAD else self.data_bus

    def signal_latch_address(self, sel, load=0):
        self.address_reg = load if sel == Signal.DIRECT_ADDRESS_LOAD else self.data_bus

    def memory_manager(self, operation):
        if operation == Signal.READ:
            self.memory_bus = self.data_memory[self.address_reg]
        elif operation == Signal.WRITE:
            self.data_memory[self.address_reg] = self.data_bus

    def signal_latch_stack(self):
        self.stack_reg = self.data_bus

    def get_reg_value(self, reg):
        return {
            Bus.ACC: self.acc,
            Bus.MEM: self.memory_bus,
            Bus.STACK: self.stack_reg
        }.get(reg)

    def execute_alu_operation(self, operation, value):
        return {
            ALU.ADD: self.data_bus + value,
            ALU.SUB: self.data_bus - value,
            ALU.MUL: self.data_bus * value,
            ALU.DIV: self.data_bus / value,
            ALU.REM: self.data_bus % value,
            ALU.INC: self.data_bus + 1,
            ALU.DEC: self.data_bus - 1
        }.get(operation)

    def alu_working(self, operation=ALU.ADD, valves=[Bus.ACC]):
        self.data_bus = self.get_reg_value(valves[0])
        if len(valves) == 1:
            return
        self.data_bus = self.execute_alu_operation(operation, valves[1])


class ControlUnit:
    data_path: DataPath = None

    ip = 0

    instructions = []

    int_address = 0

    _tick = 0

    sel_address = 0

    def __init__(self, instructions, data_path):
        self.instructions = instructions
        self.data_path = data_path

    def tick(self):
        self._tick += 1

    def execute(self):
        while self.instructions[self.ip]["opcode"] != Opcode.HALT:
            instr = self.instructions[self.ip]
            if instr["opcode"] in [Opcode.LOAD, Opcode.STORE]:
                self.decode_memory_commands(instr["opcode"], instr["arg"])
            self.ip += 1

    def decode_memory_commands(self, opcode, arg):
        if opcode == Opcode.LOAD:
            if isinstance(arg, int) or arg[0] != '*':
                self.data_path.signal_latch_acc(Signal.DIRECT_ACC_LOAD, arg)
            else:
                self.data_path.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(arg[1:]))
                self.data_path.memory_manager(Signal.READ)
                self.data_path.alu_working(valves=[Bus.MEM])
                self.data_path.signal_latch_acc(Signal.DATA_ACC_LOAD)
        elif opcode == Opcode.STORE:
            self.data_path.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(arg[1:]))
            self.data_path.alu_working()
            self.data_path.memory_manager(Signal.WRITE)
        self.tick()


if __name__ == '__main__':
    with open('out.txt', "r") as f:
        code = json.load(f)
    dp = DataPath(None, 10)
    cu = ControlUnit(code, dp)
    cu.execute()
