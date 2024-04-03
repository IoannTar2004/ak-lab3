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
    BUF = "buf"
    STACK = "stack"