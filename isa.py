class Opcode:
    LOAD = "load"
    STORE = "store"

    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    REM = "rem"
    INC = "inc"
    DEC = "dec"
    CMP = "cmp"

    IN = "in"
    OUT = "out"
    CLK = "clk"
    SIGN = "sign"

    JMP = "jmp"
    JE = "je"
    JNE = "jne"
    JGE = "jge"

    CALL = "call"
    ISR = "isr"
    RET = "ret"
    IRET = "iret"
    DI = "di"
    EI = "ei"
    INTERRUPT = "int"
    TIMER = "timer"

    POP = "pop"
    PUSH = "push"

    HALT = "halt"
