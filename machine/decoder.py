from isa import Opcode
from machine_signals import *
from logger import Logger
import re
import logging


class Decoder:
    cu = None

    opcode = None

    arg = None

    def __init__(self, control_unit, opcode, arg):
        self.cu = control_unit
        self.opcode = opcode
        self.arg = arg

    def process_relative_addressing(self):
        dp = self.cu.data_path
        dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(re.sub("\\*|\\+", "", self.arg)))
        count = self.arg.count('*') - 1
        for i in range(count):
            dp.memory_manager(Signal.READ)
            dp.alu_working(valves=[Valves.MEM])
            dp.signal_latch_regs(Signal.BUF_LATCH)
            self.cu.tick()
            if self.arg[-1] == '+' and i == 0:
                dp.alu_working(Opcode.INC, [Valves.BUF])
                dp.memory_manager(Signal.WRITE)
                self.cu.tick()

            dp.alu_working(valves=[Valves.BUF])
            self.cu.data_path.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

    def decode_memory_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.LOAD:
            if isinstance(self.arg, int):
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
            else:
                self.process_relative_addressing()
                dp.memory_manager(Signal.READ)
                dp.alu_working(valves=[Valves.MEM])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)

        elif self.opcode == Opcode.STORE:
            self.process_relative_addressing()
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

                dp.alu_working(self.opcode, [Valves.BUF, Valves.ACC])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            else:
                self.process_relative_addressing()
                dp.memory_manager(Signal.READ)
                dp.alu_working(self.opcode, [Valves.ACC, Valves.MEM])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        else:
            dp.alu_working(self.opcode)
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
        self.cu.tick()

    def decode_flow_commands(self):
        dp = self.cu.data_path
        jumps = {
            Opcode.JMP: True,
            Opcode.JGE: not dp.flags["n"],
            Opcode.JE: dp.flags["z"],
            Opcode.JNE: not dp.flags["z"]
        }
        signal = Signal.JMP_ARG if jumps[self.opcode] else Signal.NEXT_IP
        self.cu.tick()
        return signal

    def decode_subprogram_commands(self):
        dp = self.cu.data_path

        def subprogram():
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

        def ret():
            dp.alu_working(valves=[Valves.STACK])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

            dp.memory_manager(Signal.READ)
            dp.alu_working(valves=[Valves.MEM])
            self.cu.signal_latch_ip(Signal.DATA_IP)
            self.cu.tick()

            dp.alu_working(Opcode.INC, [Valves.STACK])
            dp.signal_latch_regs(Signal.STACK_LATCH)

        match self.opcode:
            case Opcode.CALL:
                subprogram()
                self.cu.signal_latch_ip(Signal.JMP_ARG, self.arg)
            case Opcode.RET:
                ret()
            case Opcode.INTERRUPT:
                self.cu.int_address = self.arg
            case Opcode.ISR:
                self.cu.ei = False
                self.cu.int_rq = False
                dp.in_interruption = True
                subprogram()
                self.cu.signal_latch_ip(Signal.INTERRUPT)
                self.cu.tick()

                Decoder(self.cu, Opcode.PUSH, 0).decode_stack_commands()
            case Opcode.IRET:
                Decoder(self.cu, Opcode.POP, 0).decode_stack_commands()
                self.cu.tick()

                ret()
                self.cu.ei = True
                dp.in_interruption = False
                Logger.info("Return from interruption!", self.cu.get_ticks())
        self.cu.tick()

    def decode_interrupt_commands(self):
        match self.opcode:
            case Opcode.EI:
                self.cu.ei = True
            case Opcode.DI:
                self.cu.ei = False
            case Opcode.INTERRUPT:
                self.cu.int_address = self.arg
            case Opcode.TIMER:
                self.cu.timer.timer_delay = self.arg
        self.cu.tick()

    def decode_stack_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.PUSH:
            dp.alu_working(Opcode.DEC, [Valves.STACK])
            dp.signal_latch_regs(Signal.STACK_LATCH)
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

            dp.alu_working()
            dp.memory_manager(Signal.WRITE)

        else:
            dp.alu_working(valves=[Valves.STACK])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

            dp.memory_manager(Signal.READ)
            dp.alu_working(valves=[Valves.MEM])
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            self.cu.tick()

            dp.alu_working(Opcode.INC, [Valves.STACK])
            dp.signal_latch_regs(Signal.STACK_LATCH)
        self.cu.tick()

    def decode_io_commands(self):
        dp = self.cu.data_path
        if self.opcode in [Opcode.IN, Opcode.OUT]:
            dp.ports.set_pin_mode(self.arg, self.opcode)
        elif self.opcode == Opcode.CLK:
            dp.acc = dp.ports.impulse(self.arg, dp.acc)
            self.cu.tick()
            dp.ports.impulse(self.arg, dp.acc)
        elif self.opcode == Opcode.SIGN:
            dp.ports.signal(self.arg, dp.acc)
        self.cu.tick()
