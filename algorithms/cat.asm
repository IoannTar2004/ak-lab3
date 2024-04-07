transfer:
    store *0
    load 0
    sign 3  ; CS = 0

    load 8  ; счётчик переданных битов
    char:
        store *1
        load *0
        clk 0
        store *0
        load *1
        dec
        cmp 0
        jne char
    load 1
    sign 3  ;CS = 1
    iret

_start:
    timer 6
    int transfer
    ei

    in 1
    out 2
    out 3
    load 1
    sign 3

    loop:
        load *0
        cmp 0
        jne loop
    end: halt
