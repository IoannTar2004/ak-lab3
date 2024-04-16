transfer:
    out 2               ; загрузка старшего бита аккумулятора в буфер вывода
    sign 0              ; сдвиг влево на 1 бит аккумулятора и регистра данных в slave, если sclk = 1
    in 1                ; загрузка бита из буфера ввода в младший бит аккумулятора
    store *3            ; сохранение результата передачи
    iret

print:
    movh                    ; смещаю младший байт [7:0] в старший байт [31:24]
    store *3                ; сохраняю передаваемый байт в ячейку 2
    load 16                 ; счётчик прерываний для передачи 8-ми битов
    store *4

    sign 3                  ; CS = 0
    ei
    char:
        load *3             ; загружаю передаваемый символ. После этой инструкции по таймеру происходит прерывание
        load *4
        dec                 ; декремент счетчика
        store *4
        jne char
    di
    sign 3                  ; CS = 1
    load *3
    cmp 0                   ; если приходит 0 со slave, значит все введенные символы переданы, и их больше не нужно сохранять в память
    je skip
    store **2+

    skip: ret

_start:
    vec                     ; вектор прерывания - 0 (в аккумуляторе изначально значение 0)
    func transfer           ; устанавливаю функцию transfer как обработчик прерывания
    store *0
    timer 7                 ; установка таймера с задержкой в 7 тактов
    sign 3

    call hello              ; сохраняю строку Hello,

    load 5
    store *1                ; сохраняю указатель на текущий символ вывода
    load 12
    store *2                ; сохраняю указатель на первый введенный символ

    call name_req           ; вывожу строку 'What is your name?'
    waiting_for_chars:      ; ожидаю ввода пользователя в бесконечном цикле
        load 1              ; передаю в slave 1, чтобы ничего лишнего не записывалось в буфер
        call print
        cmp 0               ; если со slave пришел не 0, значит пользователь ввел символы
        je waiting_for_chars

    load **1+               ; загружаю символ 'H' из строки 'Hello, '
    loop:
        call print
        load **1+           ; загружаю каждый символ из строки
        cmp 0               ; пока не закончились символы, считываю данные с spi, затем добавляю этот символ в буфер вывода
        jne loop

    load '!'
    call print              ; печатаю знак восклицания в конце
    load 0
    call print              ; передаю 0-терминатор в буфер
    halt

name_req:
    load 'W'
    call print
    load 'h'
    call print
    load 'a'
    call print
    load 't'
    call print
    load ' '
    call print

    load 'i'
    call print
    load 's'
    call print
    load ' '
    call print

    load 'y'
    call print
    load 'o'
    call print
    load 'u'
    call print
    load 'r'
    call print
    load ' '
    call print

    load 'n'
    call print
    load 'a'
    call print
    load 'm'
    call print
    load 'e'
    call print
    load '?'
    call print
    load 0
    call print
    load 10
    call print

    ret

hello:
    load 'H'
    store *5
    load 'e'
    store *6
    load 'l'
    store *7
    load 'l'
    store *8
    load 'o'
    store *9
    load ','
    store *10
    load ' '
    store *11

    ret