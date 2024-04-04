from isa import Opcode
from machine_constants import *


class Decoder:
    cu = None

    opcode = None

    arg = None

    def __init__(self, control_unit, opcode, arg):
        self.cu = control_unit
        self.opcode = opcode
        self.arg = arg

    def decode_memory_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.LOAD:
            if isinstance(self.arg, int) or self.arg[0] != '*':
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
            else:
                dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(self.arg[1:]))
                dp.memory_manager(Signal.READ)
                dp.alu_working(valves=[Valves.MEM])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        elif self.opcode == Opcode.STORE:
            dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(self.arg[1:]))
            dp.alu_working()
            dp.memory_manager(Signal.WRITE)
        self.cu.tick()

    def decode_arithmetic_commands(self):
        dp = self.cu.data_path
        if self.opcode not in [Opcode.INC, Opcode.DEC]:
            if isinstance(self.arg, int):
                dp.alu_working()
                dp.signal_latch_regs(Signal.BUF_LATCH)
                self.cu.tick()

                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
                self.cu.tick()

                if self.opcode not in [Opcode.SUB, Opcode.DIV, Opcode.REM, Opcode.CMP]:
                    dp.alu_working(self.opcode, [Valves.ACC, Valves.BUF])
                else:
                    dp.alu_working(self.opcode, [Valves.BUF, Valves.ACC])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            else:
                dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(self.arg[1:]))
                dp.memory_manager(Signal.READ)
                dp.alu_working(self.opcode, [Valves.ACC, Valves.MEM])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        else:
            dp.alu_working(self.opcode)
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        self.cu.tick()

    def decode_flow_commands(self):
        dp = self.cu.data_path
        flow = False
        if self.opcode == Opcode.JMP:
            self.cu.signal_latch_ip(Signal.JMP_ARG, self.arg)
            flow = True
        if self.opcode == Opcode.JGE and dp.flags["n"] != 1:
            self.cu.signal_latch_ip(Signal.JMP_ARG, self.arg)
            flow = True
        self.cu.tick()
        return flow

    def decode_subprogram_commands(self):
        dp = self.cu.data_path
        match self.opcode:
            case Opcode.CALL:
                dp.alu_working(Opcode.DEC, [Valves.STACK])
                dp.signal_latch_regs(Signal.STACK_LATCH)
                dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
                self.cu.tick()

                dp.alu_working()
                dp.signal_latch_regs(Signal.BUF_LATCH)

                self.cu.tick()
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.cu.ip)
                dp.alu_working()
                dp.memory_manager(Signal.WRITE)
                self.cu.tick()

                dp.alu_working(valves=[Valves.BUF])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
                self.cu.signal_latch_ip(Signal.JMP_ARG, self.arg)
            case Opcode.RET:
                dp.alu_working(valves=[Valves.STACK])
                dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
                self.cu.tick()

                dp.memory_manager(Signal.READ)
                dp.alu_working(valves=[Valves.MEM])
                self.cu.signal_latch_ip(Signal.DATA_IP)
                self.cu.tick()

                dp.alu_working(Opcode.INC, [Valves.STACK])
                dp.signal_latch_regs(Signal.STACK_LATCH)
        self.cu.tick()

    def decode_interrupt_commands(self):
        self.cu.ei = 1 if self.opcode == Opcode.EI else 0
