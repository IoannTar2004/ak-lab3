
_start:
    load -3
    loop:
        inc
        cmp 0
        jge h
        jmp loop

    h: halt