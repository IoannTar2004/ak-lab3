from machine.isa import Opcode
from machine.logger import Logger


SCLK = 0
MISO = 1
MOSI = 2
CS = 3


class Ports:

    def __init__(self, slave, code_file):
        self.tick = 0
        self.data = {SCLK: 0, MISO: 0, MOSI: 0, CS: 0}

        self.slave = slave
        self.slave.ports = self.data
        self.log = Logger(code_file, "spi")
        self.slave.log = self.log

        self.data_path = None

    def io_buffer_manager(self, opcode, port_id):
        acc = bin(self.data_path.acc)[2:].zfill(32)
        if opcode == Opcode.IN:
            acc = acc[:-1] + str(self.data[port_id])
            self.data_path.acc = int(acc, 2)
        else:
            self.data[port_id] = int(acc[0])
        self.log.debug(self, self.tick)

    def inverse_signal(self, port_id):
        self.data[port_id] = int(not self.data[port_id])
        self.log.debug(self, self.tick)

        if port_id == SCLK and self.data[port_id] == 1:
            self.shift()
        elif port_id == CS and self.data[CS] == 0:
            self.log.info("Start of character transmission", self.tick)
        elif port_id == CS and self.data[CS] == 1:
            self.slave.add_to_output_buffer()

    def shift(self):
        self.data_path.acc = (self.data_path.acc & (2**31 - 1)) << 1
        self.slave.get_impulse()
        self.log.debug(self, self.tick)

    def __repr__(self):
        bin_acc = bin(self.data_path.acc)[2:].zfill(32)
        return f"TICK: {self.tick} | SLAVE DR: {bin(self.slave.data_reg)[2:].zfill(8)} ({self.slave.data_reg}) "\
               f"<-> ACC: {bin_acc[:8]} | {bin_acc[24:]} ({int(bin_acc[:8], 2)} " \
               f"| {int(bin_acc[24:], 2)})" \
               f" | PORTS: {self.data}"


class Slave:

    def __init__(self, input_tokens):
        self.data_reg = 0
        self.output_buffer = []
        self.input_tokens = input_tokens
        self.first_cs = True
        self.can_remove_from_input = False

        self.ports = None
        self.log = None

    def add_input(self, tick):
        if len(self.input_tokens) > 0 and self.ports[CS] == 1 and tick >= self.input_tokens[0][0]:
            self.data_reg = ord(self.input_tokens[0][1])
            self.can_remove_from_input = True

    def get_impulse(self):
        binary = bin(self.data_reg)[2:].zfill(8)
        self.ports[MISO] = int(binary[0])
        binary = binary[1:] + str(self.ports[MOSI])
        self.data_reg = int(binary, 2)

    def add_to_output_buffer(self):
        if self.ports[CS] == 1:
            if self.first_cs:
                self.first_cs = False
            else:
                self.log.info("The transfer of the symbol is completed")
                if self.data_reg != 1:
                    self.output_buffer.append(chr(self.data_reg))
                    self.log.info(f"Added symbol '{chr(self.data_reg)}' to output_buffer")
                if len(self.input_tokens) > 0 and self.can_remove_from_input:
                    self.input_tokens.pop(0)
                    self.can_remove_from_input = False
                self.data_reg = 0
