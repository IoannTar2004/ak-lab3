transfer:
    store *3        ; сохраняю передаваемый байт в ячейку 2
    load 0
    sign 3          ; CS = 0

    load 8          ; счётчик переданных битов
    char:           ; цикл для передачи и получения данных от slave путем подачи тактовых импульсов командой clk на порт 0.
        store *4    ; сохраняем счетчик
        load *3     ; загружаем передаваемые биты
        clk 0       ; подача тактового импульса, инициирующий сдвиг регистров
        store *3
        load *4     ; декрементируем счетчик
        dec
        cmp 0       ; если счетчик равен нулю, значит все биты переданы
        jne char

    load *3         ; если приходит 0 со slave, значит все введенные символы переданы, и их больше не нужно сохранять в память
    cmp 0
    je skip
    store **2+      ; сохранить полученный символ по указателю в ячейке 2

    skip: load 1
    sign 3          ; CS = 1
    iret

enter_hello:
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

_start:
    vec                 ; вектор прерывания - 0 (в аккумуляторе изначально значение 0)
    func transfer       ; устанавливаю функцию transfer как обработчик прерывания
    store *0
    timer 9             ; установка таймера с задержкой в 9 тактов

    call enter_hello    ; сохраняю строку Hello,

    in 1                ; порт 1 (MISO) устанавливаю на прием данных
    out 2               ; порт 2 (MOSI) устанавливаю на передачу данных
    out 3               ; порт 3 (CS) устанавливаю на вывод сигнала
    load 1
    sign 3              ; устанавливаю cs в 1

    ei                  ; разрешаю прерывания (включаю таймер прерываний)
    load 5
    store *1           ; сохраняю указатель на текущий символ вывода
    load 12
    store *2            ; сохраняю указатель на первый введенный символ

    loop:
        load **1+       ; загружаю каждый символ из строки
        cmp 0           ; пока не передали 0-терминатор, считываю данные с spi, затем добавляю этот символ в буфер вывода и выхожу из программы
        jne loop
    end: halt