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

    JMP = "jmp"
    JE = "je"
    JNE = "jne"
    JGE = "jge"

    CALL = "call"
    FUNC = "func"
    ISR = "isr"
    RET = "ret"
    IRET = "iret"

    DI = "di"
    EI = "ei"
    VECTOR = "vec"
    TIMER = "timer"

    POP = "pop"
    PUSH = "push"

    IN = "in"
    OUT = "out"
    CLK = "clk"
    SIGN = "sign"

    HALT = "halt"
