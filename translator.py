import json
import re
from isa import Opcode


def labels_insert(labels, instructions):
    for instr in instructions:
        if "arg" in instr and instr["arg"] in labels:
            instr["arg"] = labels[instr["arg"]]


def labels_parse(labels, line, index):
    split = re.split("\s*:\s*", line)
    labels[split[0]] = index
    split.pop(0)


def translator(code):
    instructions = []
    labels = {}
    index = 0
    for line in code:
        line = line.strip()
        if len(line) == 0:
            continue

        if ":" in line:
            labels_parse(labels, line, index)
            continue
        split = re.split("(?<!')\s+(?!=')", line)
        instr = {"index": index, "opcode": split[0]}

        if len(split) > 1:
            try:
                instr["arg"] = int(split[1])
            except ValueError:
                if instr["opcode"] not in [Opcode.JMP, Opcode.JZ, Opcode.JGE] and split[1][0] != '*':
                    instr["arg"] = ord(split[1][1])
                else:
                    instr["arg"] = split[1]
        instructions.append(instr)
        index += 1
    labels_insert(labels, instructions)
    return instructions


if __name__ == '__main__':
    with open('./algorithms/test.asm') as f:
        code = f.readlines()
    instructions = translator(code)

    buf = []
    for instr in instructions:
        buf.append(json.dumps(instr))
    with open("./out.txt", "w") as f:
        f.write("[" + ",\n ".join(buf) + "]")
