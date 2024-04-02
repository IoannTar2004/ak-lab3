import re


def labels_insert(labels, instructions):
    for instr in instructions:
        if "arg" in instr and instr["arg"] in labels:
            instr["arg"] = labels[instr["arg"]]


def main():
    instructions = []
    labels = {}
    with open('./algorithms/hello.asm') as code:
        index = 0
        for line in code:
            line = line.strip()
            if len(line) == 0:
                continue

            '''парсинг меток'''
            if ":" in line:
                split = re.split("\s*:\s*", line)
                labels[split[0]] = index
                split.pop(0)
                if split[0] == '':
                    continue
                line = "".join(split)

            split = re.split("(?<!')\s+(?!=')", line)
            instr = {"index": index, "opcode": split[0]}

            if len(split) > 1:
                try:
                    instr["arg"] = int(split[1])
                except ValueError:
                    if instr["opcode"] not in ["jmp", "jz"] and split[1][0] != '*':
                        instr["arg"] = ord(split[1][1])
                    else:
                        instr["arg"] = split[1]
            instructions.append(instr)
            index += 1
    labels_insert(labels, instructions)
    for i in instructions:
        print(i)


if __name__ == '__main__':
    main()
