transfer:
    store *2            ; сохраняю передаваемый байт в ячейку 2
    load 0
    sign 3              ; CS = 0

    load 8              ; счётчик переданных битов
    char:               ; цикл для передачи и получения данных от slave путем подачи тактовых импульсов командой clk на порт 0.
        store *3
        load *2
        clk 0
        store *2
        load *3
        dec
        cmp 0
        jne char
    load 1
    sign 3              ; CS = 1
    iret

_start:
    in 1                ; порт 1 (MISO) устанавливаю на прием данных
    out 2               ; порт 2 (MOSI) устанавливаю на передачу данных
    out 3               ; порт 3 (CS) устанавливаю на вывод сигнала
    load 1
    sign 3              ; устанавливаю cs в 1

    int transfer        ; устанавливаю функцию transfer как обработчик прерывания
    timer 2             ; установка таймера с задержкой в 2 такта
    ei                  ; разрешаю прерывания (включаю таймер прерываний)

    load 'H'            ; перед прерыванием эти символы загружаются в аккумулятор
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
