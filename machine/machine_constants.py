class Signal:
    DIRECT_ACC_LOAD = 0
    DATA_ACC_LOAD = 1
    DIRECT_ADDRESS_LOAD = 3
    DATA_ADDRESS_LOAD = 4

    WRITE = 5
    READ = 6

    STACK_LATCH = 7
    BUF_LATCH = 8

    NEXT_IP = 9
    JMP_ARG = 10
    INTERRUPT = 11
    DATA_IP = 12


class Valves:
    ACC = "acc"
    MEM = "mem"
    BUF = "buf"
    STACK = "stack"
