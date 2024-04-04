from machine import *
import translator
import json


if __name__ == '__main__':
    translator.tr()
    with open("out.txt", "r", encoding="utf-8") as f:
        code = json.load(f)
    dp = DataPath(None, 10)
    cu = ControlUnit(code, dp)
    cu.execute()