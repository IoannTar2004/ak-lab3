func:
    add 10
    push
    load *3
    pop
    ret
_start:
    load -3
    call func
    halt