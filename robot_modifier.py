import re

# Порядок изменения формата хода при поворотах
ORDER_STEP_FORMAT = ((0, 1), (1, 1), (0, -1), (1, -1))  # 0 <=> x, 1 <=> y

# Символ зарисовки
PAIN_SYM = '*'

# Поддерживаемые символы:
VALID_SYMBOLS_MODIFIER = "FLR0123456789!"


def get_list_com(com_string):
    """Эта функция будет возвращать команду в виде списка.
    Пригодится если включен модификатор"""
    # Разбиваем на символы и числа в список
    com_list = re.split('([0-9][0-9][0-9]|[0-9][0-9]|[0-9]|F|R|L|!)', com_string)
    com_list = list(filter(lambda sym: sym != '', com_list))
    return com_list


def check_commands_modifier(com_string):
    """Проверка на валидность введенной команды с включенным модификатором"""
    # Проверяем, что все символы валидны
    if not set(com_string) <= set(VALID_SYMBOLS_MODIFIER):
        return {'answer': False,
                'text': 'Введен не поддерживаемый символ'}

    # Проверяем, что последний не число и первый не "!"
    # not in ("F", "L", "R", "!") - условие ищущее число
    if com_string[-1] not in ("F", "L", "R", "!") or com_string[0] == '!':
        return {'answer': False,
                'text': 'Либо число на последнем месте, либо "!" на первом'}

    # Теперь проверим, что символы чисел, стоят только перед "F" и символы "!" только после "F"
    # Разобьем строку символов на список, по буквам и проверим, что после числа стоит "F"
    com_list = get_list_com(com_string)
    for idx, sym in enumerate(com_list):
        if sym == '!':
            if com_list[idx - 1] != "F":
                return {'answer': False,
                        'text': '"!" стоит не после "F"'}

        if sym not in ("R", "L", "F", "!"):
            if com_list[idx + 1] not in ("R", "L", "F"):
                return {'answer': False,
                        'text': 'Число стоит не перед символами "F","R","L"'}
    return {'answer': True,
            'text': 'OK'}


def get_format_step(com_sym, step_format):
    """Определяем новый формат хода (coord, step)"""
    if com_sym == "L":
        idx = 1
    else:
        idx = -1

    # найдем индекс текущего формата хода в списке
    idx_format = ORDER_STEP_FORMAT.index(step_format)

    # поменяем формат по порядку на следующий или предыдущий, в зависимости от поворота
    # и не забудем поделить по модулю на его длину, для цикличного перемещения в кортеже
    step_format = ORDER_STEP_FORMAT[(idx_format + idx) % len(ORDER_STEP_FORMAT)]
    return step_format


def get_coord_list(com_string):
    """Создаем карту координат"""
    start_coord = [0, 0]
    com_list = [start_coord, ]  # первую координату [0, 0] сразу добавим в список ходов
    multiplier = 1  # множитель, нужен только в том случае, если запущена версия с модификатором
    invisible_list = []  # для скрытых ходов робота, которые не будут отражаться

    # step_format[0] - координата (x или y)
    # step_format[1] - шаг (1 или -1)
    step_format = ORDER_STEP_FORMAT[0]

    com_string = get_list_com(com_string)

    for idx, com in enumerate(com_string):
        add_invisible = False  # флаг для добавления комбинаций в лист невидимых шагов
        if com not in ("R", "L", "F", "!"):
            multiplier = int(com)

        elif com == "F":
            # адаптированное условие под модификатор
            # Если после числового запроса будет стоять "!" (3F!) надо записать как 3 невидимых хода
            if idx != len(com_string)-1:    # проверяем, не является ли индекс последним
                if com_string[idx+1] == "!":    # если нет, то является ли следующий "!"
                    add_invisible = True
            for _ in range(multiplier):
                last_coord = com_list[-1].copy()
                last_coord[step_format[0]] += step_format[1]
                com_list.append(last_coord)
                if add_invisible:
                    invisible_list.append(last_coord)
            # не забываем сбросить множитель
            multiplier = 1

        elif com in ("R", "L"):
            # в зависимости от поворота, меняем формат
            for _ in range(multiplier):
                step_format = get_format_step(com, step_format)
            multiplier = 1
    return com_list, invisible_list


def align_coord_map(coord_map, negative_coord):
    """Сдвинем значения координат, чтобы избавиться от отрицательных
        В эту функцию, мы попадаем, только если найдены отрицательные значения координат"""
    # найдем минимальные значения каждой координаты
    x_negative = min([coord[0] for coord in negative_coord])
    y_negative = min([coord[1] for coord in negative_coord])

    # Сдвигаем, с помощью добавления модуля самой меньшей отрицательной координаты
    # оба условия if, так как возможно придется сдвигать обе оси
    if x_negative < 0:
        coord_map = list(map(lambda coord: [coord[0] + abs(x_negative), coord[1]], coord_map))
    if y_negative < 0:
        coord_map = list(map(lambda coord: [coord[0], coord[1] + abs(y_negative)], coord_map))
    return coord_map


def get_negative_coord(coord_map):
    """Функция для определения отрицательных значений координат"""
    negative_coord = list(filter(lambda coord: coord[0] < 0 or coord[1] < 0, coord_map))
    if negative_coord:
        coord_map = align_coord_map(coord_map, negative_coord)
    return coord_map


def print_map(coord_map, coord_invisible):
    """Рисуем карту исход из заданных координат
        Функция адаптирована под модифицированную"""
    # Находим самую верхнюю и самую правую точки. Добавляем 1, для правильного отображения через range
    max_x = max([coord[0] for coord in coord_map]) + 1
    max_y = max([coord[1] for coord in coord_map]) + 1

    # Создаем массив пустой карты, исходя из размеров.
    # По "х" будет список столбцов, по "у" список строчек.
    map_massive = [[' ' for _ in range(max_x)] for _ in range(max_y)]

    # Отразим зеркально значения y, для правильного отображения карты.
    # В данный момент, начало координат слева сверху, а должно быть слева снизу.
    # Для этого вычтем по модулю максимальное значение "y", из каждого "у" в координатной карте,
    # перед этим не забудем уменьшить максимальное значение "у" на 1.
    coord_map = list(map(lambda coord: [coord[0], abs(coord[1] - (max_y - 1))], coord_map))

    # Если присутствуют невидимые следы
    if coord_invisible:
        coord_invisible = list(map(lambda coord: [coord[0], abs(coord[1] - (max_y - 1))], coord_invisible))

    # изменяем пробелы в массиве на "*" по заданным координатам
    for coord in coord_map:
        x, y = coord
        map_massive[y][x] = PAIN_SYM  # на первом месте "y", так как список координат "х" внутри списка "у".

    # Аналогично с невидимыми следами, если они есть. Заменяем обратно на пробел
    if coord_invisible:
        for coord in coord_invisible:
            x, y = coord
            map_massive[y][x] = " "

    # создаем объект рисунка карты
    printing_obj = ''
    for string in map_massive:
        printing_obj += ''.join(string) + '\n'
    return printing_obj


def execute(com_string):
    print()
    print(com_string)
    # поверяем команду; регистр не важен
    com_string = com_string.upper().replace(' ', '')

    check_status = check_commands_modifier(com_string)
    if not check_status['answer']:
        return check_status['text']

    # получаем карту координат робота
    coord_map, coord_invisible = get_coord_list(com_string)

    # Если в карте присутствуют отрицательные значения, то выровнять её
    coord_map = get_negative_coord(coord_map)

    # Идентично с invisible
    coord_invisible = get_negative_coord(coord_invisible)

    # Теперь рисуем саму карту
    printing_map = print_map(coord_map, coord_invisible)
    return printing_map


# ВХОДНЫЕ ДАННЫЕ
com_1 = "FFFFFLFFFFFLFFFFFLFFFFFL"
com_2 = "LFFFFFRFFFRFFFRFFFFFFF"
com_3 = "LFFFFFRFFFRFFFRFFFFFFFC"
com_4 = "1fl02fl3fl4fl5fl6fl7fl8fl9fl10fl11fl"
com_5 = "!4FL12FL4FL4FL"
com_6 = "4FL12FL4FL4FL2"
com_7 = "4FL12FL4F5L4FL"
com_8 = "4FL12FL4FL!FL"
com_9 = "FRF2L3F"
com_10 = "LLFF!RFLFF!RFLFF!RFLFF!RFLFF!RFLFF!RFLFF!RRFFF!LFRFF!LFRFF!LFRFF!LFRFF!LFRFF!RFLF!RFLF!RFL12FF!LFRF!LFRF!LFRFRF!L2FRF!L2FRF!L2FRF!L2FRF!L2FRF!R2FF!LFRFF!LFRFF!LFRFF!LFRFF!LFR15F" \
        "R2F!R12F" \
        "RR5FRFLFRFRF" \
        "L2F!R6F!3FLF!LF!17F!LFR2F"
COM_YA = "FLFRFLFRFLFRFLFFLFRFLFRFLFRFLFRFRFLFRFLFRFLFRFRFLFLFRFRFLFLFRFRFFRFLFLFRFRFLFLFRFRFLFLFRFRFLFLFRFRFLFLFRFRFRRF"

print(execute(com_1))
print(execute(com_2))
print(execute(com_3))
print(execute(com_4))
print(execute(com_5))
print(execute(com_6))
print(execute(com_7))
print(execute(com_8))
print(execute(com_9))
print(execute(com_10))
print(execute(COM_YA))
