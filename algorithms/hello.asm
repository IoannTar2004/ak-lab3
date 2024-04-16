transfer:
    out 2           ; загрузка старшего бита аккумулятора в буфер вывода
    sign 0          ; сдвиг влево на 1 бит аккумулятора и регистра данных в slave, если sclk = 1
    in 1            ; загрузка бита из буфера ввода в младший бит аккумулятора
    store *2        ; сохранение результата передачи
    iret

print:
    movh                ; смещаю младший байт [7:0] в старший байт [31:24]
    store *2            ; сохраняю передаваемый байт в ячейку 2
    load 16             ; счётчик прерываний для передачи 8-ми битов
    store *3

    sign 3              ; CS = 0
    ei                  ; разрешаю прерывания (запускаю таймер)
    char:
        load *2         ; загружаю передаваемый символ. После этой инструкции по таймеру происходит прерывание
        load *3
        dec             ; декремент счетчика
        store *3
        jne char
    di                  ; запрещаю прерывания (выключаю таймер)
    sign 3              ; CS = 1
    ret

_start:
    vec                 ; вектор прерывания - 0 (в аккумуляторе изначально значение 0)
    func transfer       ; устанавливаю функцию transfer как обработчик прерывания
    store *0
    timer 7             ; установка таймера с задержкой в 7 тактов

    sign 3              ; устанавливаю cs в 1

    load 'H'            ; загружаю символы строки 'Hello world!' в аккумулятор для передачи в slave
    call print
    load 'e'
    call print
    load 'l'
    call print
    load 'l'
    call print
    load 'o'
    call print
    load ' '
    call print

    load 'w'
    call print
    load 'o'
    call print
    load 'r'
    call print
    load 'l'
    call print
    load 'd'
    call print
    load '!'
    call print
    load 0
    call print

    halt