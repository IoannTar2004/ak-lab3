from isa import Opcode
from machine_constants import *
import translator
import json

arithmetic_operations = [Opcode.ADD, Opcode.SUB, Opcode.MUL, Opcode.DIV, Opcode.REM, Opcode.INC, Opcode.DEC, Opcode.CMP]


class DataPath:
    extern_device = None

    acc = 0

    buf_reg = 0

    stack_pointer = 0

    address_reg = 0

    memory_bus = 0

    ei = 0

    flags = {"z": False, "n": False}

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
        if Signal.BUF_LATCH in regs:
            self.buf_reg = self.data_bus
        if Signal.STACK_LATCH in regs:
            self.stack_pointer = self.data_bus

    def execute_alu_operation(self, operation, value=0):
        match operation:
            case Opcode.ADD: return self.data_bus + value
            case Opcode.SUB: return self.data_bus - value
            case Opcode.MUL: return self.data_bus * value
            case Opcode.DIV: return self.data_bus // value
            case Opcode.REM: return self.data_bus % value
            case Opcode.INC: return self.data_bus + 1
            case Opcode.DEC: return self.data_bus - 1
            case Opcode.CMP:
                self.flags = {"z": self.data_bus == value, "n": self.data_bus < value}
                return self.data_bus

    def get_bus_value(self, bus):
        match bus:
            case Bus.ACC: return self.acc
            case Bus.BUF: return self.buf_reg
            case Bus.STACK: return self.stack_pointer
            case Bus.MEM: return self.memory_bus

    def alu_working(self, operation=Opcode.ADD, valves=[Bus.ACC]):
        self.data_bus = self.get_bus_value(valves[0])
        if Bus.ACC in valves:
            self.flags = {"z": self.acc == 0, "n": self.data_bus < 0}
        if operation in [Opcode.INC, Opcode.DEC]:
            self.data_bus = self.execute_alu_operation(operation)
        elif len(valves) > 1:
            self.data_bus = self.execute_alu_operation(operation, self.get_bus_value(valves[1]))


class ControlUnit:
    data_path: DataPath = None

    ip = 0

    instructions = []

    int_address = 0

    _tick = 0


    def __init__(self, instructions, data_path):
        self.ip = instructions[0]["_start"]
        del instructions[0]
        self.instructions = instructions
        self.data_path = data_path

    def tick(self):
        self._tick += 1
        self.data_path.data_bus = 0
        self.data_path.memory_bus = 0

    def execute(self):
        while self.instructions[self.ip]["opcode"] != Opcode.HALT:
            instr = self.instructions[self.ip]
            decoder = Decoder(self, instr["opcode"], instr["arg"] if "arg" in instr else 0)
            if decoder.opcode in [Opcode.LOAD, Opcode.STORE]:
                decoder.decode_memory_commands()
            elif decoder.opcode in arithmetic_operations:
                decoder.decode_arithmetic_commands()
            elif decoder.opcode in [Opcode.JMP, Opcode.JGE]:
                if decoder.decode_flow_commands():
                    continue
            self.signal_latch_ip()

    def signal_latch_ip(self, signal=Signal.NEXT_IP, arg=0):
        match signal:
            case Signal.NEXT_IP: self.ip += 1
            case Signal.JMP_ARG: self.ip = arg
            case Signal.INTERRUPT: self.ip = self.int_address
            case Signal.DATA_IP: self.ip = self.data_path.data_bus

class Decoder:
    cu: ControlUnit = None

    opcode = None

    arg = None

    def __init__(self, control_unit, opcode, arg):
        self.cu = control_unit
        self.opcode = opcode
        self.arg = arg

    def decode_memory_commands(self):
        dp = cu.data_path
        if self.opcode == Opcode.LOAD:
            if isinstance(self.arg, int) or self.arg[0] != '*':
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
            else:
                dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(self.arg[1:]))
                dp.memory_manager(Signal.READ)
                dp.alu_working(valves=[Bus.MEM])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        elif self.opcode == Opcode.STORE:
            dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(self.arg[1:]))
            dp.alu_working()
            dp.memory_manager(Signal.WRITE)
        cu.tick()

    def decode_arithmetic_commands(self):
        dp = cu.data_path
        if self.opcode not in [Opcode.INC, Opcode.DEC]:
            if isinstance(self.arg, int):
                dp.alu_working()
                dp.signal_latch_regs(Signal.BUF_LATCH)
                cu.tick()
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
                cu.tick()
                if self.opcode not in [Opcode.SUB, Opcode.DIV, Opcode.REM, Opcode.CMP]:
                    dp.alu_working(self.opcode, [Bus.ACC, Bus.BUF])
                else:
                    dp.alu_working(self.opcode, [Bus.BUF, Bus.ACC])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            else:
                dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(self.arg[1:]))
                dp.memory_manager(Signal.READ)
                dp.alu_working(self.opcode, [Bus.ACC, Bus.MEM])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        else:
            dp.alu_working(self.opcode)
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        cu.tick()

    def decode_flow_commands(self):
        dp = cu.data_path
        match self.opcode:
            case Opcode.JMP:
                cu.signal_latch_ip(Signal.JMP_ARG, self.arg)
                return True
            case Opcode.JGE:
                if dp.flags["n"] != 1:
                    cu.signal_latch_ip(Signal.JMP_ARG, self.arg)
                    return True
        return False


if __name__ == '__main__':
    translator.tr()
    with open("out.txt", "r", encoding="utf-8") as f:
        code = json.load(f)
    dp = DataPath(None, 10)
    cu = ControlUnit(code, dp)
    cu.execute()
