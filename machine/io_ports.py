from isa import Opcode


SCLK = 0
MISO = 1
MOSI = 2
CS = 3


class Ports:
    ports_config = {SCLK: [], MISO: [], MOSI: [], CS: []}

    data = {SCLK: 0, MISO: '0', MOSI: '0', CS: 0}

    slave = None

    def __init__(self, slave):
        self.slave = slave
        self.slave.ports = self.data

    def set_pin_mode(self, port_id, io):
        self.ports_config[port_id].append(io)

    def impulse(self, port_id, acc):
        if self.data[port_id] == 0:
            self.data[port_id] = 1
            if Opcode.IN in self.ports_config[1] and Opcode.OUT in self.ports_config[2] and self.data[3] == 0:
                self.data[MOSI], bin_acc = shift(acc)
                self.slave.impulse()
                acc = int(bin_acc + self.data[MISO], 2)
                return acc
        else:
            self.data[port_id] = 0

    def signal(self, port_id, sign):
        self.data[port_id] = sign
        self.slave.add_to_output_buffer()


def shift(number):
    binary = bin(number)[2:].zfill(8)
    bit = binary[0]
    binary = binary[1:]
    return bit, binary


class Slave:
    data_reg = 0

    output_buffer = []

    input_tokens = []

    can_output = False

    ports = None

    def __init__(self, input_tokens):
        self.input_tokens = input_tokens

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
                if self.data_reg != 1:
                    self.output_buffer.append(chr(self.data_reg))
                if len(self.input_tokens) > 0:
                    self.input_tokens.pop(0)
                self.data_reg = 0
