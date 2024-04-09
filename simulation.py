import json

from machine.cpu import *


def start(code_file, machine, input_tokens, memory_capacity):
    slave = Slave(input_tokens)
    ports = Ports(slave)
    dp = DataPath(memory_capacity, ports)
    ports.data_path = dp
    cu = ControlUnit(code_file, machine, dp)

    result = cu.execute()

    cu.log.close()
    ports.log.close()

    return result


def main(code_file, input_file):
    input_tokens = []
    time = 11
    with open(input_file, "r", encoding="utf-8") as f:
        input_string = f.readline()

    for char in input_string:
        input_tokens.append((time, char))
        time += 10
    input_tokens.append((time, "\x00"))

    with open(code_file, "r", encoding="utf-8") as f:
        code = json.load(f)
    out, instr_count, tick_count = start(os.path.basename(code_file), code, input_tokens, 30)

    print(f"{out}\n")
    print(f"ticks_count: {tick_count}")
    print(f"instructions_count: {instr_count}")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: cpu.py <code_file> <input_file>"
    _, code_file, input_file = sys.argv

    main(code_file, input_file)
