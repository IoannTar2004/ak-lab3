from machine import *
import translator
import json


if __name__ == '__main__':
    translator.tr()
    input_tokens = []
    # with open("../inputs/cat.txt", "r") as f:
    #     time = 0
    #     line = f.readline()
    #     for char in line:
    #         input_tokens.append((time, char))
    #         time += 10
    # print(input_tokens)

    with open("out.txt", "r", encoding="utf-8") as f:
        code = json.load(f)
    out = simulation(code, [], 15)
    print("".join(out))
