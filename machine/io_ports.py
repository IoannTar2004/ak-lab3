from machine.isa import Opcode
from machine.logger import Logger


SCLK = 0
MISO = 1
MOSI = 2
CS = 3


class Ports:

    def __init__(self, slave):
        self.data = {SCLK: 0, MISO: '0', MOSI: '0', CS: 0}
        self.ports_config = {SCLK: [], MISO: [], MOSI: [], CS: []}

        self.slave = slave
        self.slave.ports = self.data
        self.log = Logger("logs/spi.txt", "spi")
        self.slave.log = self.log

        self.data_path = None

    def set_pin_mode(self, port_id, io):
        self.ports_config[port_id].append(io)
        self.log.debug(self)

    def impulse(self, port_id):
        if self.data[port_id] == 0:
            self.data[port_id] = 1
            if Opcode.IN in self.ports_config[1] and Opcode.OUT in self.ports_config[2] and self.data[3] == 0:
                self.data[MOSI], bin_acc = shift(self.data_path.acc)
                self.slave.impulse()
                self.data_path.acc = int(bin_acc + self.data[MISO], 2)
                self.log.debug(self)
        else:
            self.data[port_id] = 0

    def signal(self, port_id):
        self.data[port_id] = self.data_path.acc
        self.log.debug(self)
        self.slave.add_to_output_buffer()
        if self.data_path.acc == 0:
            self.log.info("Start of character transmission")

    def __repr__(self):
        return f"SLAVE DR: {bin(self.slave.data_reg)[2:].zfill(8)} ({self.slave.data_reg}) "\
               f"<-> ACC: {bin(self.data_path.acc)[2:].zfill(8)} ({self.data_path.acc})" \
               f" | PORTS: {self.data} | PORTS_CONFIG: {self.ports_config}"


def shift(number):
    binary = bin(number)[2:].zfill(8)
    bit = binary[0]
    binary = binary[1:]
    return bit, binary


class Slave:

    def __init__(self, input_tokens):
        self.data_reg = 0
        self.output_buffer = []
        self.input_tokens = input_tokens
        self.can_output = False

        self.ports = None
        self.log = None

    def add_input(self, tick):
        if len(self.input_tokens) > 0 and self.ports[CS] == 1 and tick >= self.input_tokens[0][0]:
            self.data_reg = ord(self.input_tokens[0][1])

    def impulse(self):
        if self.ports[CS] == 0 and self.ports[SCLK] == 1:
            self.ports[MISO], bin_data = shift(self.data_reg)
            self.data_reg = int(bin_data + self.ports[MOSI], 2)

    def add_to_output_buffer(self):
        if self.ports[CS] == 1:
            if not self.can_output:
                self.can_output = True
            else:
                self.log.info("The transfer of the symbol is completed")
                if self.data_reg != 1:
                    self.output_buffer.append(chr(self.data_reg))
                    self.log.info(f"Added symbol '{chr(self.data_reg)}' to output_buffer")
                if len(self.input_tokens) > 0:
                    self.input_tokens.pop(0)
                self.data_reg = 0
