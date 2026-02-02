"""
Структура вопросов чек-листа с поддержкой подпунктов
Портировано из src/data/checklistData.ts
"""

def get_checklist_questions_full():
    """Возвращает полную структуру вопросов с subOptions"""
    return [
        {
            'id': 1,
            'title': 'Сигнал звукового тона',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
            ],
        },
        {
            'id': 2,
            'title': 'Батарейка ключа',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'subOptions': [
                        {'value': 'discharged', 'label': 'Разряжена'},
                        {'value': 'missing', 'label': 'Отсутствует'},
                        {'value': 'damaged', 'label': 'Повреждена'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 3,
            'title': 'Щетки стеклоочистителя переднего',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {
                            'value': 'right',
                            'label': 'Передняя правая',
                            'subOptions': [
                                {'value': 'smearing', 'label': 'Мажет'},
                                {'value': 'damaged', 'label': 'Повреждена'},
                                {'value': 'missing', 'label': 'Отсутствует'},
                            ],
                        },
                        {
                            'value': 'left',
                            'label': 'Передняя левая',
                            'subOptions': [
                                {'value': 'smearing', 'label': 'Мажет'},
                                {'value': 'damaged', 'label': 'Повреждена'},
                                {'value': 'missing', 'label': 'Отсутствует'},
                            ],
                        },
                    ],
                },
            ],
        },
        {
            'id': 4,
            'title': 'Стекло лобовое',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'chips', 'label': 'Сколы'},
                        {'value': 'cracks', 'label': 'Трещины'},
                    ],
                },
            ],
        },
        {
            'id': 5,
            'title': 'Подсветка приборов',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
            ],
        },
        {
            'id': 6,
            'title': 'Лампы неисправностей на панели приборов',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'check_engine', 'label': 'Check Engine'},
                        {'value': 'srs', 'label': 'SRS'},
                        {'value': 'abs', 'label': 'ABS'},
                        {'value': 'battery', 'label': 'АКБ'},
                        {'value': 'hybrid', 'label': 'Hybrid System / IMA'},
                    ],
                },
            ],
        },
        {
            'id': 7,
            'title': 'Рамка переднего госномера',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
            ],
        },
        {
            'id': 8,
            'title': 'Габариты передние',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
            ],
        },
        {
            'id': 9,
            'title': 'Ближний свет',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
            ],
        },
        {
            'id': 10,
            'title': 'Дальний свет',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
            ],
        },
        {
            'id': 11,
            'title': 'Передние противотуманные фары',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 12,
            'title': 'Повороты передние',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right_main', 'label': 'Справа основной'},
                        {'value': 'right_mirror', 'label': 'Справа зеркало'},
                        {'value': 'right_wing', 'label': 'Справа крыло'},
                        {'value': 'left_main', 'label': 'Слева основной'},
                        {'value': 'left_mirror', 'label': 'Слева зеркало'},
                        {'value': 'left_wing', 'label': 'Слева крыло'},
                    ],
                },
            ],
        },
        {
            'id': 13,
            'title': 'Колесо переднее левое',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'bulges_cuts', 'label': 'Грыжи, порезы'},
                        {'value': 'valve_cracks', 'label': 'Вентиль трещины'},
                        {'value': 'pressure', 'label': 'Давление вне нормы'},
                        {'value': 'missing_nut', 'label': 'Отсутствует гайка колеса'},
                    ],
                },
            ],
        },
        {
            'id': 14,
            'title': 'Колесо заднее левое',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'bulges_cuts', 'label': 'Грыжи, порезы'},
                        {'value': 'valve_cracks', 'label': 'Вентиль трещины'},
                        {'value': 'pressure', 'label': 'Давление вне нормы'},
                        {'value': 'missing_nut', 'label': 'Отсутствует гайка колеса'},
                    ],
                },
            ],
        },
        {
            'id': 15,
            'title': 'Щетка стеклоочистителя заднего',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'subOptions': [
                        {'value': 'smearing', 'label': 'Мажет'},
                        {'value': 'worn', 'label': 'Изношена'},
                        {'value': 'missing', 'label': 'Отсутствует'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 16,
            'title': 'Рамка заднего госномера',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
            ],
        },
        {
            'id': 17,
            'title': 'Подсветка заднего госномера',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
            ],
        },
        {
            'id': 18,
            'title': 'Габариты задние',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
            ],
        },
        {
            'id': 19,
            'title': 'Повороты задние',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
            ],
        },
        {
            'id': 20,
            'title': 'Стоп сигналы задние',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'center', 'label': 'По центру'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
            ],
        },
        {
            'id': 21,
            'title': 'Сигнал заднего хода',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
            ],
        },
        {
            'id': 22,
            'title': 'Задние противотуманные фары',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'right', 'label': 'Справа'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 23,
            'title': 'Колесо заднее правое',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'bulges_cuts', 'label': 'Грыжи, порезы'},
                        {'value': 'valve_cracks', 'label': 'Вентиль трещины'},
                        {'value': 'pressure', 'label': 'Давление вне нормы'},
                        {'value': 'missing_nut', 'label': 'Отсутствует гайка колеса'},
                    ],
                },
            ],
        },
        {
            'id': 24,
            'title': 'Колесо переднее правое',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'bulges_cuts', 'label': 'Грыжи, порезы'},
                        {'value': 'valve_cracks', 'label': 'Вентиль трещины'},
                        {'value': 'pressure', 'label': 'Давление вне нормы'},
                        {'value': 'missing_nut', 'label': 'Отсутствует гайка колеса'},
                    ],
                },
            ],
        },
        {
            'id': 25,
            'title': 'Состояние приводных ремней',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {
                            'value': 'timing_belt',
                            'label': 'Ремень ГРМ',
                            'subOptions': [
                                {'value': 'cracks', 'label': 'Трещины'},
                                {'value': 'peeling', 'label': 'Отслоения'},
                                {'value': 'oil', 'label': 'Попадания масла'},
                                {'value': 'missing', 'label': 'Отсутствует'},
                            ],
                        },
                        {
                            'value': 'alternator_belt',
                            'label': 'Ремень генератора',
                            'subOptions': [
                                {'value': 'cracks', 'label': 'Трещины'},
                                {'value': 'peeling', 'label': 'Отслоения'},
                                {'value': 'oil', 'label': 'Попадания масла'},
                                {'value': 'missing', 'label': 'Отсутствует'},
                            ],
                        },
                        {
                            'value': 'power_steering_belt',
                            'label': 'Ремень ГУР',
                            'subOptions': [
                                {'value': 'cracks', 'label': 'Трещины'},
                                {'value': 'peeling', 'label': 'Отслоения'},
                                {'value': 'oil', 'label': 'Попадания масла'},
                                {'value': 'missing', 'label': 'Отсутствует'},
                            ],
                        },
                        {
                            'value': 'ac_belt',
                            'label': 'Ремень кондиционера',
                            'subOptions': [
                                {'value': 'cracks', 'label': 'Трещины'},
                                {'value': 'peeling', 'label': 'Отслоения'},
                                {'value': 'oil', 'label': 'Попадания масла'},
                                {'value': 'missing', 'label': 'Отсутствует'},
                            ],
                        },
                        {
                            'value': 'pump_belt',
                            'label': 'Ремень помпы',
                            'subOptions': [
                                {'value': 'cracks', 'label': 'Трещины'},
                                {'value': 'peeling', 'label': 'Отслоения'},
                                {'value': 'oil', 'label': 'Попадания масла'},
                                {'value': 'missing', 'label': 'Отсутствует'},
                            ],
                        },
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 26,
            'title': 'Уровень масла ДВС',
            'options': [
                {'value': 'below', 'label': 'Ниже уровня'},
                {'value': '0-25', 'label': '0-25%'},
                {'value': '25-50', 'label': '25-50%'},
                {'value': '50-75', 'label': '50-75%'},
                {'value': '75-100', 'label': '75-100%'},
                {'value': 'above', 'label': 'Выше уровня'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 27,
            'title': 'Состояние масла ДВС',
            'options': [
                {'value': 'fresh', 'label': 'Свежее'},
                {'value': 'working', 'label': 'Рабочее'},
                {'value': 'particles', 'label': 'С примесями'},
            ],
        },
        {
            'id': 28,
            'title': 'Уровень жидкости ГУР',
            'options': [
                {'value': 'below', 'label': 'Ниже уровня'},
                {'value': '50-75', 'label': '50-75%'},
                {'value': '75-100', 'label': '75-100%'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 29,
            'title': 'Состояние жидкости ГУР',
            'options': [
                {'value': 'fresh', 'label': 'Свежее'},
                {'value': 'working', 'label': 'Рабочее'},
                {'value': 'burnt', 'label': 'Горелое'},
            ],
        },
        {
            'id': 30,
            'title': 'Уровень охлаждающей жидкости ДВС',
            'options': [
                {'value': 'below', 'label': 'Ниже уровня'},
                {'value': 'level', 'label': 'Уровень'},
                {'value': 'above', 'label': 'Выше уровня'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 31,
            'title': 'Цвет охлаждающей жидкости ДВС',
            'options': [
                {'value': 'red', 'label': 'Красный'},
                {'value': 'green', 'label': 'Зеленый'},
                {'value': 'blue', 'label': 'Синий'},
            ],
        },
        {
            'id': 32,
            'title': 'Состояние охлаждающей жидкости ДВС',
            'options': [
                {'value': 'clean', 'label': 'Чистая'},
                {'value': 'cloudy', 'label': 'Мутная'},
            ],
        },
        {
            'id': 33,
            'title': 'Температура кристаллизации ОЖ ДВС',
            'options': [
                {'value': '25_35', 'label': '-25-35°С'},
                {'value': '35_45', 'label': '-35-45°С'},
                {'value': 'more_45', 'label': 'Более -45°С'},
            ],
        },
        {
            'id': 34,
            'title': 'Уровень охлаждающей жидкости HV',
            'options': [
                {'value': 'below', 'label': 'Ниже уровня'},
                {'value': 'level', 'label': 'Уровень'},
                {'value': 'above', 'label': 'Выше уровня'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 35,
            'title': 'Цвет охлаждающей жидкости HV',
            'options': [
                {'value': 'red', 'label': 'Красный'},
                {'value': 'green', 'label': 'Зеленый'},
                {'value': 'blue', 'label': 'Синий'},
            ],
        },
        {
            'id': 36,
            'title': 'Состояние охлаждающей жидкости HV',
            'options': [
                {'value': 'clean', 'label': 'Чистая'},
                {'value': 'cloudy', 'label': 'Мутная'},
            ],
        },
        {
            'id': 37,
            'title': 'Температура кристаллизации ОЖ HV',
            'options': [
                {'value': '25_35', 'label': '-25-35°С'},
                {'value': '35_45', 'label': '-35-45°С'},
                {'value': 'more_45', 'label': 'Более -45°С'},
            ],
        },
        {
            'id': 38,
            'title': 'Уровень охлаждающей жидкости турбины',
            'options': [
                {'value': 'below', 'label': 'Ниже уровня'},
                {'value': 'level', 'label': 'Уровень'},
                {'value': 'above', 'label': 'Выше уровня'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 39,
            'title': 'Цвет охлаждающей жидкости турбины',
            'options': [
                {'value': 'red', 'label': 'Красный'},
                {'value': 'green', 'label': 'Зеленый'},
                {'value': 'blue', 'label': 'Синий'},
            ],
        },
        {
            'id': 40,
            'title': 'Состояние охлаждающей жидкости турбины',
            'options': [
                {'value': 'clean', 'label': 'Чистая'},
                {'value': 'cloudy', 'label': 'Мутная'},
            ],
        },
        {
            'id': 41,
            'title': 'Температура кристаллизации ОЖ турбины',
            'options': [
                {'value': '25_35', 'label': '-25-35°С'},
                {'value': '35_45', 'label': '-35-45°С'},
                {'value': 'more_45', 'label': 'Более -45°С'},
            ],
        },
        {
            'id': 42,
            'title': 'Уровень тормозной жидкости',
            'options': [
                {'value': 'below', 'label': 'Ниже уровня'},
                {'value': 'level', 'label': 'Уровень'},
                {'value': 'above', 'label': 'Выше уровня'},
            ],
        },
        {
            'id': 43,
            'title': 'Температура кипения тормозной жидкости',
            'options': [
                {'value': 'less_180', 'label': 'Менее 180°С'},
                {'value': 'more_180', 'label': 'Более 180°С'},
            ],
        },
        {
            'id': 44,
            'title': 'Состояние тормозной жидкости',
            'options': [
                {'value': 'clean', 'label': 'Чистая'},
                {'value': 'cloudy', 'label': 'Мутная'},
            ],
        },
        {
            'id': 45,
            'title': 'Уровень масла КПП',
            'options': [
                {'value': 'below', 'label': 'Ниже уровня'},
                {'value': '50-75', 'label': '50-75%'},
                {'value': '75-100', 'label': '75-100%'},
                {'value': 'need_disassembly', 'label': 'Требуется разбор'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 46,
            'title': 'Состояние масла КПП',
            'options': [
                {'value': 'fresh', 'label': 'Свежее'},
                {'value': 'working', 'label': 'Рабочее'},
                {'value': 'burnt', 'label': 'Горелое'},
            ],
        },
        {
            'id': 47,
            'title': 'Омывающая жидкость',
            'options': [
                {'value': 'present', 'label': 'Присутствует'},
                {'value': 'missing', 'label': 'Отсутствует'},
                {'value': 'frozen', 'label': 'Замерзла'},
            ],
        },
        {
            'id': 48,
            'title': 'Работа стартера при запуске ДВС',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'noise', 'label': 'Посторонний шум'},
                        {'value': 'long_start', 'label': 'Длительный запуск'},
                        {'value': 'jamming', 'label': 'Заклинивание'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 49,
            'title': 'Работа ДВС',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'uneven', 'label': 'Неровная работа'},
                        {'value': 'noise', 'label': 'Посторонний шум'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 50,
            'title': 'Работа КПП',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'jolts', 'label': 'Пинки / Толчки'},
                        {'value': 'noise', 'label': 'Посторонний шум'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 51,
            'title': 'Течи технических жидкостей',
            'options': [
                {'value': 'no_leaks', 'label': 'Нет течей'},
                {
                    'value': 'has_leaks',
                    'label': 'Есть течи',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'valve_cover', 'label': 'Течь клапанной крышки'},
                        {'value': 'turbo', 'label': 'Течь турбокомпрессора'},
                        {'value': 'oil_cooler', 'label': 'Течь охладителя масла'},
                        {'value': 'brake_fluid', 'label': 'Течь тормозной жидкости'},
                        {'value': 'coolant', 'label': 'Течь антифриза'},
                    ],
                },
            ],
        },
        {
            'id': 52,
            'title': 'Состояние воздушного фильтра',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'dirty', 'label': 'Загрязнен'},
                        {'value': 'moisture', 'label': 'Попадание влаги'},
                    ],
                },
                {'value': 'need_disassembly', 'label': 'Требуется разбор'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 53,
            'title': 'Состояние салонного фильтра',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'dirty', 'label': 'Загрязнен'},
                        {'value': 'moisture', 'label': 'Попадание влаги'},
                    ],
                },
                {'value': 'need_disassembly', 'label': 'Требуется разбор'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 54,
            'title': 'Состояние фильтра ВВБ',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'dirty', 'label': 'Загрязнен'},
                        {'value': 'moisture', 'label': 'Попадание влаги'},
                    ],
                },
                {'value': 'need_disassembly', 'label': 'Требуется разбор'},
                {'value': 'na', 'label': 'Не предусмотрено'},
            ],
        },
        {
            'id': 55,
            'title': 'Иные замечания',
            'options': [
                {'value': 'complete', 'label': 'Завершить, замечаний нет'},
            ],
        },
    ]