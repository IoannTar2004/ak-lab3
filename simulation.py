import json
import os
import sys

from machine.cpu import DataPath, ControlUnit
from machine.io_ports import Ports, Slave


def start(code_file, machine, input_tokens, memory_capacity):
    slave = Slave(input_tokens)
    ports = Ports(slave, code_file)
    dp = DataPath(memory_capacity, ports)
    ports.data_path = dp
    cu = ControlUnit(code_file, machine, dp)

    result = cu.execute()

    cu.log.close()
    ports.log.close()

    return result


def get_tokens(input_file):
    with open(input_file, "r", encoding="utf-8") as f:
        input_string = f.readline()

    input_tokens = []
    match os.path.basename(input_file):
        case "hello_user_name.txt":
            time = 8157
            offset = 100
        case _:
            time = 11
            offset = 100

    for char in input_string:
        input_tokens.append((time, char))
        time += offset
    input_tokens.append((time, "\x00"))
    return input_tokens


def main(code_file, input_file):
    input_tokens = get_tokens(input_file)

    with open(code_file, "r", encoding="utf-8") as f:
        code = json.load(f)
    out, instr_count, tick_count = start(os.path.basename(code_file), code, input_tokens, 100)

    if len(out) > 0:
        print(f"{out}\n")
    print(f"ticks_count: {tick_count}")
    print(f"instructions_count: {instr_count}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: cpu.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv

    main(code_file, input_file)
