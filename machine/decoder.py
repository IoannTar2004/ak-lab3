from machine.isa import Opcode
from machine.machine_signals import Signal, Operands
import re


class Decoder:

    def __init__(self, control_unit, opcode, arg):
        self.cu = control_unit
        self.opcode = opcode
        self.arg = arg

    def process_addressing(self):
        dp = self.cu.data_path
        dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, int(re.sub("\\*|\\+", "", self.arg)))
        count = self.arg.count('*') - 1
        for i in range(count):
            dp.memory_manager(Signal.READ)
            dp.alu_working(valves=[Operands.MEM])
            dp.signal_latch_regs(Signal.BUF_LATCH)
            self.cu.tick()
            if self.arg[-1] == '+' and i == 0:
                dp.alu_working(Opcode.INC, [Operands.BUF])
                dp.memory_manager(Signal.WRITE)
                self.cu.tick()

            dp.alu_working(valves=[Operands.BUF])
            self.cu.data_path.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

    def decode_memory_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.LOAD:
            if isinstance(self.arg, int):
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
            else:
                self.process_addressing()
                dp.memory_manager(Signal.READ)
                dp.alu_working(valves=[Operands.MEM])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)

        elif self.opcode == Opcode.STORE:
            self.process_addressing()
            dp.alu_working()
            dp.memory_manager(Signal.WRITE)
        self.cu.tick()

    def decode_arithmetic_commands(self):
        dp = self.cu.data_path
        if self.opcode not in [Opcode.INC, Opcode.DEC, Opcode.MOVH]:
            if isinstance(self.arg, int):
                dp.alu_working()
                dp.signal_latch_regs(Signal.BUF_LATCH)
                self.cu.tick()

                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
                self.cu.tick()

                dp.alu_working(self.opcode, [Operands.BUF, Operands.ACC])
                dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            else:
                self.process_addressing()
                dp.memory_manager(Signal.READ)
                dp.alu_working(self.opcode, [Operands.ACC, Operands.MEM])
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
        self.cu.tick()
        signal = Signal.JMP_ARG if jumps[self.opcode] else Signal.NEXT_IP
        self.cu.tick()
        return signal

    def decode_subprogram_commands(self):
        dp = self.cu.data_path

        def subprogram():
            dp.alu_working(Opcode.DEC, [Operands.STACK])
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

            dp.alu_working(valves=[Operands.BUF])
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)

        def ret():
            dp.alu_working(valves=[Operands.STACK])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

            dp.memory_manager(Signal.READ)
            dp.alu_working(valves=[Operands.MEM])
            self.cu.signal_latch_ip(Signal.DATA_IP)
            self.cu.tick()

            dp.alu_working(Opcode.INC, [Operands.STACK])
            dp.signal_latch_regs(Signal.STACK_LATCH)

        match self.opcode:
            case Opcode.CALL:
                subprogram()
                self.cu.signal_latch_ip(Signal.JMP_ARG, self.arg)
            case Opcode.RET:
                ret()
            case Opcode.ISR:
                if self.cu.ei and self.cu.int_rq:
                    self.cu.ei = False
                    self.cu.int_rq = False
                    dp.in_interruption = True
                    subprogram()
                    self.cu.tick()

                    Decoder(self.cu, Opcode.PUSH, 0).decode_stack_commands()

                    dp.signal_latch_address(Signal.DIRECT_ADDRESS_LOAD, self.cu.int_vector)
                    dp.memory_manager(Signal.READ)
                    dp.alu_working(valves=[Operands.MEM])
                    self.cu.signal_latch_ip(Signal.DATA_IP)
            case Opcode.IRET:
                Decoder(self.cu, Opcode.POP, 0).decode_stack_commands()

                ret()
                self.cu.ei = True
                dp.in_interruption = False
                self.cu.log.info("Return from interruption!", self.cu.get_ticks())
            case Opcode.FUNC:
                dp.signal_latch_acc(Signal.DIRECT_ACC_LOAD, self.arg)
        self.cu.tick()

    def decode_interrupt_commands(self):
        match self.opcode:
            case Opcode.EI:
                self.cu.ei = True
            case Opcode.DI:
                self.cu.ei = False
                self.cu.timer.time = -2
            case Opcode.VECTOR:
                dp = self.cu.data_path
                dp.alu_working()
                self.cu.int_vector = dp.alu_out
            case Opcode.TIMER:
                self.cu.timer.timer_delay = self.arg
        self.cu.tick()

    def decode_stack_commands(self):
        dp = self.cu.data_path
        if self.opcode == Opcode.PUSH:
            dp.alu_working(Opcode.DEC, [Operands.STACK])
            dp.signal_latch_regs(Signal.STACK_LATCH)
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

            dp.alu_working()
            dp.memory_manager(Signal.WRITE)

        else:
            dp.alu_working(valves=[Operands.STACK])
            dp.signal_latch_address(Signal.DATA_ADDRESS_LOAD)
            self.cu.tick()

            dp.memory_manager(Signal.READ)
            dp.alu_working(valves=[Operands.MEM])
            dp.signal_latch_acc(Signal.DATA_ACC_LOAD)
            self.cu.tick()

            dp.alu_working(Opcode.INC, [Operands.STACK])
            dp.signal_latch_regs(Signal.STACK_LATCH)
        self.cu.tick()

    def decode_io_commands(self):
        dp = self.cu.data_path
        dp.ports.tick = self.cu.get_ticks()
        if self.opcode in [Opcode.IN, Opcode.OUT]:
            dp.ports.io_buffer_manager(self.opcode, self.arg)
        else:
            dp.ports.inverse_signal(self.arg)
        self.cu.tick()
