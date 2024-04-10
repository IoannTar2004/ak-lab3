# Лабораторная работа №3 по Архитектуре Компьютера

- Тарасов Иван Сергеевич. P3230
- `asm | acc | harv | hw | tick | struct | trap | port | cstr | prob2 | spi`
- Усложнённый вариант

## Язык программирования - Assembly
```
program ::= { line }

line ::= label [ comment ] "\n"
       | instr [ comment ] "\n"
       | [ comment ] "\n"

label ::= label_name ":"

instr ::= op0
        | op1 integer
        | op1 char
        | op1 address
        | op2 address
        | op3 arg
        | op4 label_name

op0 ::= "inc"
      | "dec"
      | "halt"
      | "ei"
      | "di"
      | "pop"
      | "push"
      | "ret"
      | "iret"
      | "vec"

op1 ::= | "store"
        | "add"
        | "sub"
        | "mul"
        | "div"
        | "rem"
        | "cmp"
   
op2 ::= "store"
      
op3 ::= "in"
      | "out"
      | "timer"
      | "clk"
      | "sign"

op4 ::= "jmp"
      | "je"
      | "jne"
      | "jge"
      | "call"
      | "func"

integer ::= [ "-" ] { <any of "0-9"> }-

char ::= '<"a-z A-z">'

address ::= <any of *> { <any of "0-9"> }

arg ::= <any of "0-9">

label_name ::= <any of "a-z A-Z _"> { <any of "a-z A-Z 0-9 _"> }

comment ::= ";" <any symbols except "\n">
```
**Операции:**

_Операции с памятью:_
- `load` - загружает в аккумулятор указанное в аргументе число или значение из указанной ячейки памяти
- `store` - сохраняет в память значение из аккумулятора по указанной ячейке памяти

_Арифметические операции (результат записывается в аккумулятор):_
- `add` - произвести сложение аккумулятора с указанным числом или значением из указанной ячейки памяти
- `sub` - произвести вычитание указанного числа или значения из указанной ячейки памяти из аккумулятора
- `mul` - произвести умножение аккумулятора на указанное число или значение из указанной ячейки памяти
- `div` - произвести деление аккумулятора на указанное число или значение из указанной ячейки памяти
- `rem` - вычисление остатка от деления аккумулятора на указанное число или значение из указанной ячейки памяти
- `inc` - инкремент аккумулятора
- `dec` - декремент аккумулятора
- `cmp` - установить флаги по вычитанию указанного числа или значения из указанной ячейки памяти из аккумулятора

_Инструкции перехода_:
- `jmp` - безусловный переход на метку
- `je` - переход на метку, если флаг 'Z' равен 1. Переход, если равно
- `jne` - переход на метку, если флаг 'Z' равен 0. Переход, если не равно
- `jge` - переход на метку, если флаг 'N' равен 0. Переход, если больше или равно

_Инструкции подпрограмм_:
- `call` - переход на подпрограмму. Добавление в стек адреса возврата из подпрограммы
- `ret` - возврат из подпрограммы. Восстановление IP из стека
- `iret` - возврат из прерывания. Восстановление аккумулятора и IP. Разрешение прерываний
- `func` - записывает в аккумулятор адрес указанной функции

_Инструкции настройки прерываний:_
- `ei` - разрешить прерывания (включить таймер прерываний)
- `di` - запретить прерывания (выключить таймер прерываний)
- `vec` - установить вектор прерывания по значению в аккумуляторе
- `timer` - установить задержку для таймера прерываний

_Операции со стеком:_
- `push` - записать в стек значение аккумулятора
- `pop` - записать в аккумулятор значение из вершины стека

_Операции ввода-вывода:_
- `in` - настроить порт, адрес которого указан в аргументе, на ввод
- `out` - настроить порт, адрес которого указан в аргументе, на вывод
- `clk` - подать тактовый импульс на порт, адрес которого указан в аргументе,
- `sign` - подать сигнал на порт, адрес которого указан в аргументе. В качестве сигнала выступает значение
аккумулятора (0 или 1)


- `halt` - остановить процессор

**Метки**

Метки для переходов могут определяться как на отдельных строчках, так и слева от инструкци:
```
label: load 0

label:
   load 0
```

На этапе трансляции в инструкции перехода, а также в инструкции "func" и "call", вместо меток подставляются
указатель на инструкции в памяти команд.

```jmp label ; -> jmp 10```

## Организация памяти

Модель памяти процессора:
1. Память команд и данных разделены (Гарвардская архитектура)
2. Память команд. Машинное слово - не определено. Реализуется списком словарей, описывающих инструкции 
(одно слово - одна ячейка).
3. Память данных. Машинное слово - 4 байта, знаковое. Реализуется списком чисел.
4. Система команд выстроена вокруг аккумулятора (acc), поэтому программисту доступен только этот регистр.
Также имеются несколько команд (in, out, timer, clk, ei, di, halt), которые не используют аккумулятор.
5. Программист может обращаться только к памяти данных, однако инструкции перехода, func и call в некотором
смысле позволяют взаимодействовать с памятью инструкций.
6. Для реализации подпрограмм и для удобства присутствует указатель стека (SP), который указывает на конец
памяти данных.

```
 Registers
+------------------------------+
| acc                          |
+------------------------------+

 Instruction memory
+------------------------------+
| 00  : instruction            |
| 01  : instruction            |
|             ...              |
| n   : program start          |
|             ...              |
| i   : instruction            |
| i+1 : instruction            |
|             ...              |
+------------------------------+

  Data memory
+------------------------------+
| 00  : variable/int_vector    |
| 01  : variable               |
|    ...                       |
| i-1 : variable               |
| i   : variable               |
+------------------------------+

  Interruption controller
+------------------------------+
| interruption_vector: vector  |
+------------------------------+
```

Главное применение стека в моем варианте - работа с прерываниями. Во время перехода на прерывание,
в стек помещается адрес инструкции, после которого произошло прерывание, а за ним помещается и значение
из аккумулятора. По возращению из прерывания сначала восстанавливается аккумулятор, затем адрес
инструкции.

**Адресация**

Операции с памятью и арифметические операции поддерживают 4 типа адресации. 
1. <ins>Прямая загрузка</ins>: **instr 10**. Значением выступает просто константа, указанная в 
аргументе инструкции. Можно указать символ в одинарных кавычках (актуально для load). Его код будет
использоваться в качестве значения.
   - **load 10** - загружает в аккумулятор число 10.
   - **load 'H'** - загружает в аккумулятор код символа 'H' - 72.
   - **add 10** - производит сложение аккумулятора с числом 10.
2. <ins>Абсолютная адресация</ins>: **instr \*10**. Значением выступает содержимое из ячейки памяти, 
указанной после символа \*.
   - **load \*10** - загружает в аккумулятор значение из 10-ой ячейки памяти. 
   - **add \*10** - производит сложение аккумулятора со значением из 10-ой ячейки.
3. <ins>Косвенная адресация</ins>: **instr \*\*10**. Значением выступает содержимое ячейки памяти, 
указатель которой лежит в другой ячейке, указанная после звездочек. Можно указывать больше двух звездочек, 
тем самым, наращивая уровень косвенности.
   - **load \*\*10** - загружает в аккумулятор значение из ячейки памяти, указатель которой 
    находится в ячейке 10. 
   - **add \*\*10** - производит сложение аккумулятора со значением из ячейки памяти, указатель которой 
    находится в ячейке 10. 
4. <ins>Косвенная автоинкрементая адресация</ins>: **instr \*\*10+**. Работает также, как и косвенная 
адресация, но после получения содержимого ячейки инкрементирует указатель, лежащий в указанной в аргументе 
ячейке. Используется для реализации автоматического указателя.
   - **load \*\*10+** - загружает в аккумулятор значение из ячейки памяти, указатель которой 
   находится в ячейке 10, инкрементируя указатель в 10-ой ячейке. 
   - **add \*\*10+** - производит сложение аккумулятора со значением из ячейки памяти, указатель которой 
   находится в ячейке 10, инкрементируя указатель в 10-ой ячейке.

Инструкция "store" не поддерживает прямую загрузку!

## Система команд

### Особенности процессора

- Машинное слово данных - 4 байта. Операции с памятью и арифметические операции поддерживают все 4 типа адресации.

- Есть 4 регистра: аккумулятор (acc) - единственный регистр, доступный программисту, буферный регистр (buf_reg) -
в него записываются промежуточные результаты во время выполнения инструкций. Реализован мною для удобства. Третий
регистр - стековый регистр (stack_pointer) - указатель на нижнюю часть памяти данных. Используется для переходов
на подпрограммы, но также и для удобства. Последний регистр - адресный регистр (address_reg), который указывает
на ячейку памяти данных, из которой читаются или в которую записываются данные.
- Все регистры и вывод из памяти (memory_bus) приходят на АЛУ. АЛУ может пропустить данные с одной из шин, а также
произвести математическую операцию с одной или двумя шинами. Вывод с АЛУ попадает на шину alu_out, данные
на которой можно записать в любой регистр. Также вывод АЛУ используется для установки вектора прерываний и для
изменения IP.
- Ввод-вывод осуществляется через порты, каждый из которых имеет свой адрес, токенизирован, символьный. 
Каждый символ имеет расписание ввода.
- Поток управления:
  - инкремент IP после каждой инструкции;
  - переходы на инструкции осуществляются инструкциями перехода, командой call и вызовом прерывания.

### Набор инструкций

- A (Argument) - аргумент инструкции. Для операций с памятью и арифметических операций - прямая загрузка
- M (Memory) - значение из памяти
- <sup>n</sup>*M - значение из памяти по указателю, лежащего в памяти (косвенная адресация) с уровнем
косвенности n.

**Операции с памятью**

| Инструкция |       Адресация       |  Кол-во тактов  | Мнемоника                        |
|------------|:---------------------:|:---------------:|----------------------------------|
| load       |    Прямая загрузка    |        1        | A -> ACC                         |
| load       |      Абсолютная       |        1        | M -> ACC                         | 
| load       |       Косвенная       |     2n + 1      | <sup>n</sup>*M -> ACC            |
| load       |  Косвенная автоинкр.  |     2n + 2      | <sup>n</sup>*M -> ACC, М = М + 1 |
| store      |      Абсолютная       |        1        | ACC -> M                         | 
| store      |       Косвенная       |     2n + 1      | ACC -> <sup>n</sup>*M            |
| store      |  Косвенная автоинкр.  |     2n + 2      | ACC -> <sup>n</sup>*M, M = M + 1 |

**Арифметические операции**

| Инструкция |    Адресация    | Кол-во тактов | Мнемоника                   |
|------------|:---------------:|:-------------:|-----------------------------|
| add        | Прямая загрузка |       3       | ACC = ACC + A               |
| sub        | Прямая загрузка |       3       | ACC = ACC - A               |
| mul        | Прямая загрузка |       3       | ACC = ACC * A               |
| div        | Прямая загрузка |       3       | ACC = ACC / A               |
| rem        | Прямая загрузка |       3       | ACC = ACC % A               |
| cmp        | Прямая загрузка |       3       | Установить флаги по ACC - A |
| inc        |        -        |       1       | ACC = ACC + 1               |
| dec        |        -        |       1       | ACC = ACC - 1               |

| Инструкция |      Адресация      | Кол-во тактов | Мнемоника                             |
|------------|:-------------------:|:-------------:|---------------------------------------|
| add        |     Абсолютная      |       1       | ACC = ACC + M                         |
| add        |      Косвенная      |    2n + 1     | ACC = ACC + <sup>n</sup>*M            |
| add        | Косвенная автоинкр. |    2n + 2     | ACC = ACC + <sup>n</sup>*M, М = М + 1 |

Аналогично с другими арифметическими операциями, кроме inc и dec

**Инструкции перехода**

- L (Label) - адрес инструкции по его метке
- IP (Instruction Pointer) - указатель на текущую инструкцию

| Инструкция | Кол-во тактов | Мнемоника        |
|------------|:-------------:|------------------|
| jmp        |       1       | L -> IP          |
| je         |       1       | if Z==1: L -> IP |
| jne        |       1       | if Z==0: L -> IP |
| jge        |       1       | if N==0: L -> IP |

**Инструкции подпрограмм**

- SP (Stack Pointer) - указатель стека. Звездочка означает обращение по указателю в памяти
- EI - разрешение прерываний

| Инструкция                  | Кол-во тактов | Мнемоника                                                        |
|-----------------------------|:-------------:|------------------------------------------------------------------|
| call                        |       4       | SP = SP - 1, IP -> *SP, L -> IP                                  |
| func                        |       1       | L -> ACC                                                         |
| переход на прерывание (isr) |       7       | EI = 0, SP = SP - 1, IP -> *SP, SP = SP - 1, ACC -> *SP, L -> IP |
| ret                         |       3       | *SP -> IP, SP = SP + 1                                           |
| iret                        |       4       | *SP -> ACC, SP = SP + 1, *SP -> IP, SP = SP + 1, EI = 1          |

**Инструкции настройки прерываний:**

- V (Vector) - вектор прерываний
- T (Timer) - задержка таймера прерываний

| Инструкция | Кол-во тактов | Мнемоника |
|------------|:-------------:|-----------|
| ei         |       1       | EI = 1    |
| di         |       1       | EI = 0    |
| vec        |       1       | ACC -> V  |
| timer      |       1       | T = A     |

**Операции со стеком:**

| Инструкция | Кол-во тактов | Мнемоника               |
|------------|:-------------:|-------------------------|
| push       |       2       | SP = SP - 1, ACC -> *SP |
| pop        |       3       | *SP -> ACC, SP = SP + 1 |

**Операции ввода-вывода:**

- P(A) - порт с адресом A, где A - аргумент инструкции
- IN - настройка порта на ввод данных
- OUT - настройка порта на вывод данных
- IMP - подать тактовый импульс на порт
- [0-1] - значение от 0 до 1

| Инструкция | Кол-во тактов | Мнемоника        |
|------------|:-------------:|------------------|
| in         |       1       | P(A) = IN        |
| out        |       1       | P(A) = OUT       |
| clk        |       2       | IMP -> P(A)      |
| sign       |       1       | ACC[0-1] -> P(A) |

| Инструкция | Кол-во тактов | Мнемоника            |
|------------|:-------------:|----------------------|
| halt       |       0       | Остановка процессора |

В файле [isa.py](https://github.com/IoannTar2004/ak-lab3/blob/main/machine/isa.py) указана инструкция "isr",
которая совершает переход на подпрограмму обработки прерывания. Теоретически она может использоваться как
инструкция, однако это бессмысленно. Я добавил ее, чтобы не усложнять код.

**Машинные инструкции**

- Машинный код сериализуется в список JSON.
- Один элемент списка - одна инструкция.
- Индекс списка - адрес инструкции. Используется для команд перехода и переходов на подпрограммы. 
- В начале списка инструкций хранится строка с индексом
входа в программу (ключ "_start").
```
 [{
    "_start": 15
 },
 {
    "index": 0, 
    "opcode": "store", 
    "arg": "*2"
 },
 ...]
```
- index - адрес инструкции
- opcode - строка с кодом операции;
- arg - аргумент (может отсутствовать);

Все инструкции описаны в файле [isa.py](https://github.com/IoannTar2004/ak-lab3/blob/main/machine/isa.py) в классе
Opcode.

## Транслятор

Интерфейс командной строки: translator.py <input_file> <target_file>

Реализовано в модуле: [translator.py](https://github.com/IoannTar2004/ak-lab3/blob/main/translator.py)

Алгоритм трансляции:
1. Дроблю каждую строку на слова по пробелам.
2. Если строка пустая или содержит просто комментарий, перехожу к следующей строке.
3. Если в строке присутствует символ ":", то записываю метку в словарь с ключом метки и со значением текущего индекса.
4. Если метка называется как _start (вход в программу), то сохраняю индекс отдельно.
5. Формирование машинной инструкции с ключами index, opcode.
6. Если аргумент - число или указатель, то просто записываю его в arg, если символ, то записываю в arg его код.
7. Прохожусь по машинным инструкциям во второй раз и подставляю вместо меток индексы инструкций.

## Модель процессора

Интерфейс командной строки: machine.py <machine_code_file> <input_file>

### ControlUnit

![control_unit](https://github.com/IoannTar2004/ak-lab3/blob/main/schemes/control_unit.png)

Реализован в классе ```ControlUnit``` в модуле [cpu.py](https://github.com/IoannTar2004/ak-lab3/blob/main/machine/cpu.py).

Hardwired (реализовано полностью на Python).
- Цикл симуляции осуществляется в метод ```execute```.
- В методе ```execute``` вызываются методы класса ```Decoder```, формирующие управляющие сигналы и данные в 
DataPath и выполняющие инструкции процессора. Класс ```Decoder``` реализован в модуле
[decoder.py](https://github.com/IoannTar2004/ak-lab3/blob/main/machine/decoder.py).
- Отсчет времени работы ведется в тактах. После каждого такта (вариант _tick_) в логовый файл 
[processor.txt](https://github.com/IoannTar2004/ak-lab3/blob/main/machine/logs/processor.txt) добавляется информация
о состоянии процессора. Состояние процессора показывает:
    - текущую инструкцию
    - время в тактах
    - значения регистров
    - данные на шинах (alu_out и memory_out)
    - флаги
    - разрешены ли прерывания
    - вектор прерывания
    - задержка таймера прерываний
- Логирование осуществляется с использованием модуля **logging**. Для логирования реализован класс ```Logger``` в
модуле [logger.py](https://github.com/IoannTar2004/ak-lab3/blob/main/machine/logger.py) для более умной работы с
логом.
- Процессор выполняет инструкции, пока не дойдет до инструкции halt.
- В Control Unit содержатся таймер прерываний, в который приходят 2 шины: 
  - задержка
  - разрешение прерываний. Включает/отключает таймер

- А также контроллер прерываний, в который записывается вектор прерываний, пришедший по шине данных с DataPath.

**Сигналы**
- ```sel_address``` - выбирается адрес следующий команды. Реализующий метод - ```signal_latch_ip```.
- ```int_rq``` - запрос на прерывание. Если true, то обрабатывается после окончания работы инструкции.

### DataPath

![DataPath](https://github.com/IoannTar2004/ak-lab3/blob/main/schemes/data_path.png)

Реализован в классе ```DataPath``` в модуле [cpu.py](https://github.com/IoannTar2004/ak-lab3/blob/main/machine/cpu.py).

- Управляющие сигналы и данные на шинах поступают с декодера

**Сигналы**

Все сигналы хранятся в модуле [machine_signals.py](https://github.com/IoannTar2004/ak-lab3/blob/main/machine/machine_signals.py)
- ```latch_acc/buf/stack/address```. Защелкивают значения с шин в регистры.
  - ```signal_latch_acc``` - для аккумулятора
  - ```signal_latch_address``` - для адресного регистра
  - ```signal_latch_regs``` - для буферного регистра и указателя стека
- ```sel_acc/address``` - сигналы на соответствующие мультиплексоры. Выбирают либо пропустить значения с шин из декодера
или из ```alu_out```.

**Шины**
- Есть две входных шин данных, которые приходят с декодера:
  - ```load_acc```. Используется для прямой загрузки в аккумулятор
  - ```load_address```. Загружает значение ячейки памяти, указанной в аргументе инструкции
- И две выходных шин:
  - ```alu_out```. В ControlUnit называется ```data```
  - ```flags```. По значению флагов происходят условные переходы. Поступают на декодер.
