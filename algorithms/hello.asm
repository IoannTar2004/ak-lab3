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
    in 1
    out 2
    out 3
    load 1
    sign 3

    int print
    timer 2
    ei

    load 'H'
    load 'e'
    load 'l'
    load 'l'
    load 'o'
    load ' '

    load 'w'
    load 'o'
    load 'r'
    load 'l'
    load 'd'
    load '!'
    load 0

    halt
