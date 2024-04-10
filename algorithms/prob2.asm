; функция, которая складывает число с общей суммой, если оно четное
check_value_for_add:
    push
    rem 2
    cmp 0
    jne skip_add

    pop
    push
    add *2
    store *2

    skip_add: pop
    ret

fibonacci:
    load 2          ; загрузка первых символов последовательности Фибоначчи
    store *0
    store *2

    load 1
    add *0
    store *1

    loop:
        add *0
        store *0        ; ячейка памяти для числа с индексом i - 2
        cmp 4000000     ; пока текущее число последовательности меньше 4 млн, продолжаю алгоритм
        jge end
        call check_value_for_add

        add *1
        store *1        ; ячейка памяти для числа с индексом i - 1
        cmp 4000000
        jge end
        call check_value_for_add

        jmp loop
    end: load *2
    ret

_start:
    call fibonacci
    halt
