# Алгоритм интерпретатора команд для робота:
#     - Проверить валидность заданной команды, чтобы не было лишних символов;
#     - Создать карту координат перемещения робота;
#     - Если присутствуют отрицательные координаты:
#         то сдвинуть значения координат;
#     - нарисовать карту.


# В ходе анализа поворотов, был найден определенный порядок изменения координат
# Порядок смены хода по координатам при поворотах налево формата (coord, step):
# ((x, +1), (y, +1), (x, -1), (y, -1)).
# то есть, при начальном ходе - "x" будет увеличиваться на 1. При первом
# повороте налево - "y" будет увеличиваться на 1. При последующем - "x" будет уменьшаться на 1,
# при последнем - "y" будет уменьшаться на 1
# При поворотах направо - обратный порядок


# Порядок изменения формата хода при поворотах
ORDER_STEP_FORMAT = ((0, 1), (1, 1), (0, -1), (1, -1))  # 0 <=> x, 1 <=> y

# Символ зарисовки
PAIN_SYM = '*'

# Поддерживаемые символы:
VALID_SYMBOLS = 'FLR'


def check_commands(com_string):
    """Проверка на валидность введенной команды"""
    if not set(com_string) <= set(VALID_SYMBOLS):
        return False
    return True


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

    # step_format[0] - координата (x или y)
    # step_format[1] - шаг (1 или -1)
    step_format = ORDER_STEP_FORMAT[0]

    for com in com_string:
        if com == "F":
            # получаем последнюю координату
            last_coord = com_list[-1].copy()
            # изменяем ее по формату, и записываем в конец (Так было без множителя)
            last_coord[step_format[0]] += step_format[1]
            com_list.append(last_coord)
        else:
            # в зависимости от поворота, меняем формат
            step_format = get_format_step(com, step_format)
    return com_list


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


def not_negative_coord(coord_map):
    """Функция для определения отрицательных значений координат"""
    negative_coord = list(filter(lambda coord: coord[0] < 0 or coord[1] < 0, coord_map))
    if negative_coord:
        coord_map = align_coord_map(coord_map, negative_coord)
    return coord_map


def print_map(coord_map):
    """Рисуем карту исход из заданных координат"""
    # Находим самую верхнюю и самую правую точки. Добавляем 1, для правильного отображения через range
    max_x = max([coord[0] for coord in coord_map]) + 1
    max_y = max([coord[1] for coord in coord_map]) + 1

    # Создаем массив пустой карты, исходя из размеров.
    # По "х" будет список столбцов, по "у" список строчек.
    map_massive = [[' ' for x in range(max_x)] for _ in range(max_y)]

    # Отразим зеркально значения y, для правильного отображения карты.
    # В данный момент, начало координат слева сверху, а должно быть слева снизу.
    # Для этого вычтем по модулю максимальное значение "y", из каждого "у" в координатной карте,
    # перед этим не забудем уменьшить максимальное значение "у" на 1.
    coord_map = list(map(lambda coord: [coord[0], abs(coord[1] - (max_y - 1))], coord_map))

    # изменяем пробелы в массиве на "*" по заданным координатам
    for coord in coord_map:
        x, y = coord
        map_massive[y][x] = PAIN_SYM  # на первом месте "y", так как список координат "х" внутри списка "у".

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

    if not check_commands(com_string):
        return "Формат команды неверный"

    # получаем карту координат робота
    coord_map = get_coord_list(com_string)

    # Если в карте присутствуют отрицательные значения, то выровнять её
    coord_map = not_negative_coord(coord_map)

    # Теперь рисуем саму карту
    printing_map = print_map(coord_map)
    return printing_map


# ВХОДНЫЕ ДАННЫЕ
com_1 = "FFFFFLFFFFFLFFFFFLFFFFFL"
com_2 = "LFFFFFRFFFRFFFRFFFFFFF"
com_3 = "LFFFFFRFFFRFFFRFFFFFFFC"

COM_YANDEX = "FLFRFLFRFLFRFLFFLFRFLFRFLFRFLFRFRFLFRFLFRFLFRFRFLFLFRFRFLFLFRFRFFRFLFLFRFRFLFLFRFRFLFLFRFRFLFLFRFRFLFLFRFRFRRF" \

print(execute(com_1))
print(execute(com_2))
print(execute(com_3))

print(execute(COM_YANDEX))
