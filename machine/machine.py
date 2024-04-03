from isa import Opcode
from machine_constants import *
import json

arithmetic_operations = [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.REM, Opcode.INC, Opcode.DEC]
class DataPath:
    extern_device = None

    acc = 0

    buf_reg = 0

    stack_pointer = 0

    address_reg = 0

    memory_bus = None

    ei = 0

    data_bus = 0

    def __init__(self, extern_device, memory_capacity):
        self.data_memory = [13] * memory_capacity
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

    def signal_latch_regs(self, *regs):
        if Bus.BUF in regs:
            self.buf_reg = self.data_bus
        if Bus.STACK in regs:
            self.stack_pointer = self.data_bus

    def execute_alu_operation(self, operation, value):
        match operation:
            case Opcode.ADD: return self.data_bus + value
            case Opcode.SUB: return self.data_bus - value
            case Opcode.MUL: return self.data_bus * value
            case Opcode.DIV: return self.data_bus / value
            case Opcode.REM: return self.data_bus % value
            case Opcode.INC: return self.data_bus + 1
            case Opcode.DEC: return self.data_bus - 1

    def alu_working(self, operation=Opcode.ADD, valves=[acc]):
        self.data_bus = valves[0]
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
        self.data_path.data_bus = 0
        self.data_path.memory_bus = 0

    def execute(self):
        while self.instructions[self.ip]["opcode"] != Opcode.HALT:
            instr = self.instructions[self.ip]
            if instr["opcode"] in [Opcode.LOAD, Opcode.STORE]:
                self.decode_memory_commands(instr["opcode"], instr["arg"])
            elif instr["opcode"] in arithmetic_operations:
                self.decode_arithmetic_commands(instr["opcode"], instr["arg"])
            self.ip += 1

    def decode_memory_commands(self, opcode, arg):
        dp = self.data_path
        if opcode == Opcode.LOAD:
            if isinstance(arg, int) or arg[0] != '*':
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, arg)
            else:
                dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(arg[1:]))
                dp.memory_manager(Signal.READ)
                dp.alu_working(valves=[dp.memory_bus])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        elif opcode == Opcode.STORE:
            dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(arg[1:]))
            dp.alu_working()
            dp.memory_manager(Signal.WRITE)
        self.tick()

    def decode_arithmetic_commands(self, opcode, arg):
        dp = self.data_path
        if isinstance(arg, int):
            dp.alu_working()
            dp.signal_latch_regs(Bus.BUF)
            self.tick()
            dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, arg)
            self.tick()
            dp.alu_working(opcode, [dp.acc, dp.buf_reg])
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        else:
            dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(arg[1:]))
            dp.memory_manager(Signal.READ)
            dp.alu_working(opcode, [dp.acc, dp.memory_bus])
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        self.tick()


if __name__ == '__main__':
    with open('../out.txt', "r") as f:
        code = json.load(f)
    dp = DataPath(None, 10)
    cu = ControlUnit(code, dp)
    cu.execute()
