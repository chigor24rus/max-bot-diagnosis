"""
Структура вопросов чек-листа с поддержкой подпунктов
Полностью синхронизировано с src/data/checklistData.ts
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 5,
            'title': 'Подсветка приборов',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 7,
            'title': 'Рамка переднего госномера',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                        {'value': 'damaged', 'label': 'Повреждена'},
                        {'value': 'missing', 'label': 'Отсутствует'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 16,
            'title': 'Рамка заднего госномера',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                        {'value': 'center', 'label': 'Центральный'},
                        {'value': 'left', 'label': 'Слева'},
                    ],
                },
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
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
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 27,
            'title': 'Состояние масла ДВС',
            'options': [
                {'value': 'fresh', 'label': 'Свежее'},
                {'value': 'working', 'label': 'Рабочее'},
                {'value': 'particles', 'label': 'С механическими примесями'},
                {'value': 'water', 'label': 'Примеси воды / антифриза'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 28,
            'title': 'Тормозная жидкость / жидкость сцепления',
            'options': [
                {'value': '0-25', 'label': '0-25%'},
                {'value': '25-50', 'label': '25-50%'},
                {'value': '50-75', 'label': '50-75%'},
                {'value': '75-100', 'label': '75-100%'},
                {'value': 'above', 'label': 'Выше уровня'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 29,
            'title': 'Состояние тормозной жидкости / жидкости сцепления',
            'options': [
                {'value': 'transparent', 'label': 'Прозрачная'},
                {'value': 'dark', 'label': 'Темная'},
                {'value': 'mechanical', 'label': 'С механическими примесями'},
                {'value': 'water', 'label': 'Примеси воды / антифриза'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 30,
            'title': 'Омывающая жидкость лобового стекла',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'low', 'label': 'Низкий уровень'},
                        {'value': 'leaking', 'label': 'Течь'},
                        {'value': 'empty', 'label': 'Отсутствует'},
                    ],
                },
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 31,
            'title': 'Цвет антифриза (красный)',
            'options': [
                {'value': 'red', 'label': 'Красный'},
                {'value': 'pink', 'label': 'Розовый'},
                {'value': 'brown', 'label': 'Коричневый'},
                {'value': 'yellow', 'label': 'Желтый'},
                {'value': 'colorless', 'label': 'Бесцветный'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 32,
            'title': 'Состояние антифриза (красный)',
            'options': [
                {'value': 'transparent', 'label': 'Прозрачный'},
                {'value': 'rusty', 'label': 'Ржавый'},
                {'value': 'oily', 'label': 'Маслянистый'},
                {'value': 'particles', 'label': 'Посторонние частицы'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 33,
            'title': 'Температура замерзания антифриза (красный)',
            'options': [
                {'value': 'below_minus_25', 'label': 'Менее -25⁰С'},
                {'value': 'minus_25_to_minus_15', 'label': 'От -25⁰С до -15⁰С'},
                {'value': 'minus_15_to_minus_5', 'label': 'От -15⁰С до -5⁰С'},
                {'value': 'minus_5_to_0', 'label': 'От -5⁰С до 0⁰С'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 34,
            'title': 'Уровень антифриза (красный)',
            'options': [
                {'value': 'ok', 'label': 'В норме'},
                {'value': 'low', 'label': 'Низкий'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 35,
            'title': 'Цвет антифриза (зеленый)',
            'options': [
                {'value': 'green', 'label': 'Зеленый'},
                {'value': 'light_green', 'label': 'Светло-зеленый'},
                {'value': 'brown', 'label': 'Коричневый'},
                {'value': 'yellow', 'label': 'Желтый'},
                {'value': 'colorless', 'label': 'Бесцветный'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 36,
            'title': 'Состояние антифриза (зеленый)',
            'options': [
                {'value': 'transparent', 'label': 'Прозрачный'},
                {'value': 'rusty', 'label': 'Ржавый'},
                {'value': 'oily', 'label': 'Маслянистый'},
                {'value': 'particles', 'label': 'Посторонние частицы'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 37,
            'title': 'Температура замерзания антифриза (зеленый)',
            'options': [
                {'value': 'below_minus_25', 'label': 'Менее -25⁰С'},
                {'value': 'minus_25_to_minus_15', 'label': 'От -25⁰С до -15⁰С'},
                {'value': 'minus_15_to_minus_5', 'label': 'От -15⁰С до -5⁰С'},
                {'value': 'minus_5_to_0', 'label': 'От -5⁰С до 0⁰С'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 38,
            'title': 'Уровень антифриза (зеленый)',
            'options': [
                {'value': 'ok', 'label': 'В норме'},
                {'value': 'low', 'label': 'Низкий'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 39,
            'title': 'Цвет антифриза (синий)',
            'options': [
                {'value': 'blue', 'label': 'Синий'},
                {'value': 'light_blue', 'label': 'Светло-синий'},
                {'value': 'brown', 'label': 'Коричневый'},
                {'value': 'yellow', 'label': 'Желтый'},
                {'value': 'colorless', 'label': 'Бесцветный'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 40,
            'title': 'Состояние антифриза (синий)',
            'options': [
                {'value': 'transparent', 'label': 'Прозрачный'},
                {'value': 'rusty', 'label': 'Ржавый'},
                {'value': 'oily', 'label': 'Маслянистый'},
                {'value': 'particles', 'label': 'Посторонние частицы'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 41,
            'title': 'Температура замерзания антифриза (синий)',
            'options': [
                {'value': 'below_minus_25', 'label': 'Менее -25⁰С'},
                {'value': 'minus_25_to_minus_15', 'label': 'От -25⁰С до -15⁰С'},
                {'value': 'minus_15_to_minus_5', 'label': 'От -15⁰С до -5⁰С'},
                {'value': 'minus_5_to_0', 'label': 'От -5⁰С до 0⁰С'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 42,
            'title': 'Уровень антифриза (синий)',
            'options': [
                {'value': 'ok', 'label': 'В норме'},
                {'value': 'low', 'label': 'Низкий'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 43,
            'title': 'Уровень жидкости ГУР',
            'options': [
                {'value': 'ok', 'label': 'В норме'},
                {'value': 'low', 'label': 'Низкий'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 44,
            'title': 'Состояние жидкости ГУР',
            'options': [
                {'value': 'transparent', 'label': 'Прозрачная'},
                {'value': 'dark', 'label': 'Темная'},
                {'value': 'particles', 'label': 'Посторонние частицы'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 45,
            'title': 'Уровень масла в АКПП / Вариатор',
            'options': [
                {'value': '0-25', 'label': '0-25%'},
                {'value': '25-50', 'label': '25-50%'},
                {'value': '50-75', 'label': '50-75%'},
                {'value': '75-100', 'label': '75-100%'},
                {'value': 'above', 'label': 'Выше уровня'},
                {'value': 'need_disassembly', 'label': 'Требуется разбор'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 46,
            'title': 'Состояние масла в АКПП / Вариатор',
            'options': [
                {'value': 'transparent', 'label': 'Прозрачное'},
                {'value': 'dark', 'label': 'Темное'},
                {'value': 'burnt', 'label': 'Подгоревшее'},
                {'value': 'mechanical', 'label': 'С механическими примесями'},
                {'value': 'water', 'label': 'Примеси воды / антифриза'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 47,
            'title': 'Проверка ДВС на посторонние шумы',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'timing_chain', 'label': 'Цепь / ремень ГРМ'},
                        {'value': 'valves', 'label': 'Клапана'},
                        {'value': 'bearings', 'label': 'Подшипники навесного'},
                        {'value': 'knocking', 'label': 'Стук в двигателе'},
                    ],
                },
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 48,
            'title': 'Проверка АКПП / Вариатор',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'slipping', 'label': 'Пробуксовка'},
                        {'value': 'jerking', 'label': 'Рывки'},
                        {'value': 'noises', 'label': 'Посторонние шумы'},
                        {'value': 'error', 'label': 'Ошибка'},
                    ],
                },
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 49,
            'title': 'АКБ',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'discharged', 'label': 'Разряжена'},
                        {'value': 'swollen', 'label': 'Вздута'},
                        {'value': 'terminals', 'label': 'Окислены клеммы'},
                        {'value': 'leaking', 'label': 'Течь'},
                    ],
                },
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 50,
            'title': 'Проверка работы кондиционера',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
                {'value': 'na', 'label': 'Не предусмотрено'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 51,
            'title': 'Проверка работы отопителя',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {'value': 'bad', 'label': 'Неисправно'},
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 52,
            'title': 'Утечки из системы ДВС',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'engine_oil', 'label': 'Моторное масло'},
                        {'value': 'transmission_oil', 'label': 'Трансмиссионное масло'},
                        {'value': 'coolant', 'label': 'Антифриз'},
                        {'value': 'power_steering', 'label': 'Жидкость ГУР'},
                        {'value': 'brake_fluid', 'label': 'Тормозная жидкость'},
                        {'value': 'missing', 'label': 'Отсутствует'},
                    ],
                },
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
        {
            'id': 53,
            'title': 'Утечки из системы выхлопа',
            'options': [
                {'value': 'ok', 'label': 'Исправно'},
                {
                    'value': 'bad',
                    'label': 'Неисправно',
                    'allowMultiple': True,
                    'subOptions': [
                        {'value': 'exhaust_manifold', 'label': 'Выпускной коллектор'},
                        {'value': 'catalyst', 'label': 'Катализатор'},
                        {'value': 'resonator', 'label': 'Резонатор'},
                        {'value': 'muffler', 'label': 'Глушитель'},
                        {'value': 'missing', 'label': 'Отсутствует'},
                    ],
                },
                {'value': 'other', 'label': 'Иное (указать текстом)'},
            ],
        },
    ]