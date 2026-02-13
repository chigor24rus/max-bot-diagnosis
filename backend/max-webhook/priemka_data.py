"""
Структура вопросов чек-листа Приемки автомобиля.
Синхронизировано с src/data/priemka-checklist.ts

Типы вопросов:
- photo: требуется фото (обязательное)
- choice: выбор из вариантов (с возможностью фото)
- text_choice: выбор с возможным текстовым вводом
"""

_PRIEMKA_CACHE = None

def get_priemka_questions():
    global _PRIEMKA_CACHE

    if _PRIEMKA_CACHE is not None:
        return _PRIEMKA_CACHE

    _PRIEMKA_CACHE = [
        {
            'id': 1,
            'title': 'Фото номерного знака автомобиля',
            'type': 'photo',
        },
        {
            'id': 2,
            'title': 'Фото всей передней части автомобиля',
            'type': 'photo',
        },
        {
            'id': 3,
            'title': 'Фото лобового стекла',
            'type': 'photo',
        },
        {
            'id': 4,
            'title': 'Фото переднее левое крыло',
            'type': 'photo',
        },
        {
            'id': 5,
            'title': 'Фото передняя левая дверь',
            'type': 'photo',
        },
        {
            'id': 6,
            'title': 'Фото задняя левая дверь',
            'type': 'choice',
            'options': [
                {'value': 'not_applicable', 'label': 'Не предусмотрено'},
            ],
            'allow_photo': True,
        },
        {
            'id': 7,
            'title': 'Фото заднее левое крыло',
            'type': 'photo',
        },
        {
            'id': 8,
            'title': 'Фото всей задней части автомобиля',
            'type': 'photo',
        },
        {
            'id': 9,
            'title': 'Фото заднее правое крыло',
            'type': 'photo',
        },
        {
            'id': 10,
            'title': 'Фото задняя правая дверь',
            'type': 'choice',
            'options': [
                {'value': 'not_applicable', 'label': 'Не предусмотрено'},
            ],
            'allow_photo': True,
        },
        {
            'id': 11,
            'title': 'Фото передняя правая дверь',
            'type': 'photo',
        },
        {
            'id': 12,
            'title': 'Фото переднее правое крыло',
            'type': 'photo',
        },
        {
            'id': 13,
            'title': 'Фото крыши автомобиля',
            'type': 'photo',
        },
        {
            'id': 14,
            'title': 'Фото наружных повреждённых элементов крупно',
            'type': 'photo',
        },
        {
            'id': 15,
            'title': 'Фото дверной карты водительской двери',
            'type': 'photo',
        },
        {
            'id': 16,
            'title': 'Фото водительского сиденья, включая ножной коврик',
            'type': 'photo',
        },
        {
            'id': 17,
            'title': 'Фото переднего пассажирского сиденья, включая ножной коврик',
            'type': 'photo',
        },
        {
            'id': 18,
            'title': 'Фото панели приборов при заведённом автомобиле, наличие горящих ламп неисправностей',
            'type': 'photo',
        },
        {
            'id': 19,
            'title': 'Фото показаний одометра (Общий пробег)',
            'type': 'photo',
        },
        {
            'id': 20,
            'title': 'Дополнительные фото при необходимости',
            'type': 'choice',
            'options': [
                {'value': 'no_extra', 'label': 'Доп. фото нет'},
            ],
            'allow_photo': True,
        },
        {
            'id': 21,
            'title': 'Иные замечания',
            'type': 'text_choice',
            'options': [
                {'value': 'add_notes', 'label': 'Добавить замечания (текстом)'},
                {'value': 'complete', 'label': 'Завершить, замечаний нет'},
            ],
        },
    ]

    return _PRIEMKA_CACHE