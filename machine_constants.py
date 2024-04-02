class Signal:
    DIRECT_ACC_LOAD = 0
    DATA_ACC_LOAD = 1
    DIRECT_ADDRESS_LOAD = 3
    DATA_ADDRESS_LOAD = 4

    WRITE = 5
    READ = 6

    STACK_LATCH = 7


class Bus:
    ACC = "acc"
    MEM = "mem"
    STACK = "stack"


class ALU:

    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3
    REM = 4
    INC = 5
    DEC = 6