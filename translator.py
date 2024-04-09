import json
import re
import sys

from machine.isa import Opcode

start = 0
commands_with_labels = [Opcode.JMP, Opcode.JGE, Opcode.JE, Opcode.JNE, Opcode.CALL, Opcode.INTERRUPT]


def labels_insert(labels, instructions):
    for instr in instructions:
        if "arg" in instr and instr["arg"] in labels:
            instr["arg"] = labels[instr["arg"]]


def labels_parse(labels, line, index):
    split = re.split("\\s*:\\s*", line)
    if split[0] == "_start":
        global start
        start = index
    labels[split[0]] = index
    if split[1] == '':
        return True
    return False


def translator(source):
    instructions = []
    labels = {}
    index = 0
    for i, line in enumerate(source):
        line = line.strip()
        line = re.sub("\\s*;.*", "", line)
        if len(line) == 0 or line[0] == ';':
            continue

        if ":" in line:
            if labels_parse(labels, line, index):
                continue
        line = re.sub("\\w+:\\s*", "", line)
        split = re.split("(?<!')\\s+(?!=')", line)
        instr = {"index": index, "opcode": split[0]}

        if len(split) > 1:
            try:
                instr["arg"] = int(split[1])
            except ValueError:
                if instr["opcode"] not in commands_with_labels and split[1][0] != '*':
                    instr["arg"] = ord(split[1][1])
                else:
                    instr["arg"] = split[1]
        instructions.append(instr)
        index += 1
    labels_insert(labels, instructions)
    return instructions


def main(code, target):
    with open(code, "r") as f:
        code = f.readlines()
    instructions = translator(code)

    buf = [json.dumps({"_start": start})]
    for instr in instructions:
        buf.append(json.dumps(instr))
    with open(target, "w") as f:
        f.write("[" + ",\n ".join(buf) + "]")


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)
