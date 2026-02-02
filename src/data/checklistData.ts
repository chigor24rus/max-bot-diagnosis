export type AnswerOption = {
  value: string;
  label: string;
  requiresText?: boolean;
  requiresPhoto?: boolean;
  allowMultiple?: boolean;
  subOptions?: AnswerOption[];
  skipToQuestion?: number;
};

export type ChecklistQuestion = {
  id: number;
  title: string;
  answerType: 'single' | 'multiple';
  requiresPhoto?: boolean;
  options: AnswerOption[];
};

export const checklistQuestions: ChecklistQuestion[] = [
  {
    id: 1,
    title: 'Сигнал звукового тона',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      { value: 'bad', label: 'Неисправно' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 2,
    title: 'Батарейка ключа',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        requiresPhoto: false,
        subOptions: [
          { value: 'discharged', label: 'Разряжена', requiresPhoto: false },
          { value: 'missing', label: 'Отсутствует', requiresPhoto: false },
          { value: 'damaged', label: 'Повреждена', requiresPhoto: false },
        ],
      },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 3,
    title: 'Щетки стеклоочистителя переднего',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        subOptions: [
          {
            value: 'right',
            label: 'Передняя правая',
            requiresPhoto: false,
            subOptions: [
              { value: 'smearing', label: 'Мажет' },
              { value: 'damaged', label: 'Повреждена' },
              { value: 'missing', label: 'Отсутствует' },
            ],
          },
          {
            value: 'left',
            label: 'Передняя левая',
            requiresPhoto: false,
            subOptions: [
              { value: 'smearing', label: 'Мажет' },
              { value: 'damaged', label: 'Повреждена' },
              { value: 'missing', label: 'Отсутствует' },
            ],
          },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 4,
    title: 'Стекло лобовое',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        requiresPhoto: false,
        allowMultiple: true,
        subOptions: [
          { value: 'chips', label: 'Сколы', requiresPhoto: false },
          { value: 'cracks', label: 'Трещины', requiresPhoto: false },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 5,
    title: 'Подсветка приборов',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'ok', label: 'Исправно' },
      { value: 'bad', label: 'Неисправно' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 6,
    title: 'Лампы неисправностей на панели приборов',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'check_engine', label: 'Check Engine' },
          { value: 'srs', label: 'SRS' },
          { value: 'abs', label: 'ABS' },
          { value: 'battery', label: 'АКБ' },
          { value: 'hybrid', label: 'Hybrid System / IMA' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 7,
    title: 'Рамка переднего госномера',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'ok', label: 'Исправно' },
      { value: 'bad', label: 'Неисправно' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 8,
    title: 'Габариты передние',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 9,
    title: 'Ближний свет',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 10,
    title: 'Дальний свет',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 11,
    title: 'Передние противотуманные фары',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 12,
    title: 'Повороты передние',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right_main', label: 'Справа основной' },
          { value: 'right_mirror', label: 'Справа зеркало' },
          { value: 'right_wing', label: 'Справа крыло' },
          { value: 'left_main', label: 'Слева основной' },
          { value: 'left_mirror', label: 'Слева зеркало' },
          { value: 'left_wing', label: 'Слева крыло' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 13,
    title: 'Колесо переднее левое',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'bulges_cuts', label: 'Грыжи, порезы' },
          { value: 'valve_cracks', label: 'Вентиль трещины' },
          { value: 'pressure', label: 'Давление вне нормы' },
          { value: 'missing_nut', label: 'Отсутствует гайка колеса' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 14,
    title: 'Колесо заднее левое',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'bulges_cuts', label: 'Грыжи, порезы' },
          { value: 'valve_cracks', label: 'Вентиль трещины' },
          { value: 'pressure', label: 'Давление вне нормы' },
          { value: 'missing_nut', label: 'Отсутствует гайка колеса' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 15,
    title: 'Щетка стеклоочистителя заднего',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        requiresPhoto: false,
        subOptions: [
          { value: 'smearing', label: 'Мажет' },
          { value: 'damaged', label: 'Повреждена' },
          { value: 'missing', label: 'Отсутствует' },
        ],
      },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 16,
    title: 'Рамка заднего госномера',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'ok', label: 'Исправно' },
      { value: 'bad', label: 'Неисправно' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 17,
    title: 'Подсветка заднего госномера',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 18,
    title: 'Габариты задние',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 19,
    title: 'Повороты задние',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 20,
    title: 'Стоп сигналы задние',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'center', label: 'Центральный' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 21,
    title: 'Сигнал заднего хода',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 22,
    title: 'Задние противотуманные фары',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'right', label: 'Справа' },
          { value: 'left', label: 'Слева' },
        ],
      },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 23,
    title: 'Колесо заднее правое',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'bulges_cuts', label: 'Грыжи, порезы' },
          { value: 'valve_cracks', label: 'Вентиль трещины' },
          { value: 'pressure', label: 'Давление вне нормы' },
          { value: 'missing_nut', label: 'Отсутствует гайка колеса' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 24,
    title: 'Колесо переднее правое',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'bulges_cuts', label: 'Грыжи, порезы' },
          { value: 'valve_cracks', label: 'Вентиль трещины' },
          { value: 'pressure', label: 'Давление вне нормы' },
          { value: 'missing_nut', label: 'Отсутствует гайка колеса' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 25,
    title: 'Состояние приводных ремней',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        subOptions: [
          {
            value: 'timing_belt',
            label: 'Ремень ГРМ',
            requiresPhoto: false,
            subOptions: [
              { value: 'cracks', label: 'Трещины' },
              { value: 'peeling', label: 'Отслоения' },
              { value: 'oil', label: 'Попадания масла' },
              { value: 'missing', label: 'Отсутствует' },
            ],
          },
          {
            value: 'alternator_belt',
            label: 'Ремень генератора',
            requiresPhoto: false,
            subOptions: [
              { value: 'cracks', label: 'Трещины' },
              { value: 'peeling', label: 'Отслоения' },
              { value: 'oil', label: 'Попадания масла' },
              { value: 'missing', label: 'Отсутствует' },
            ],
          },
          {
            value: 'power_steering_belt',
            label: 'Ремень ГУР',
            requiresPhoto: false,
            subOptions: [
              { value: 'cracks', label: 'Трещины' },
              { value: 'peeling', label: 'Отслоения' },
              { value: 'oil', label: 'Попадания масла' },
              { value: 'missing', label: 'Отсутствует' },
            ],
          },
          {
            value: 'ac_belt',
            label: 'Ремень кондиционера',
            requiresPhoto: false,
            subOptions: [
              { value: 'cracks', label: 'Трещины' },
              { value: 'peeling', label: 'Отслоения' },
              { value: 'oil', label: 'Попадания масла' },
              { value: 'missing', label: 'Отсутствует' },
            ],
          },
          {
            value: 'pump_belt',
            label: 'Ремень помпы',
            requiresPhoto: false,
            subOptions: [
              { value: 'cracks', label: 'Трещины' },
              { value: 'peeling', label: 'Отслоения' },
              { value: 'oil', label: 'Попадания масла' },
              { value: 'missing', label: 'Отсутствует' },
            ],
          },
        ],
      },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 26,
    title: 'Уровень масла ДВС',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'below', label: 'Ниже уровня' },
      { value: '0-25', label: '0-25%' },
      { value: '25-50', label: '25-50%' },
      { value: '50-75', label: '50-75%' },
      { value: '75-100', label: '75-100%' },
      { value: 'above', label: 'Выше уровня' },
      { value: 'na', label: 'Не предусмотрено', skipToQuestion: 28 },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 27,
    title: 'Состояние масла ДВС',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'fresh', label: 'Свежее' },
      { value: 'working', label: 'Рабочее' },
      { value: 'particles', label: 'С механическими примесями' },
      { value: 'water', label: 'Примеси воды / антифриза' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 28,
    title: 'Уровень жидкости ГУР',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'below', label: 'Ниже уровня' },
      { value: '0-25', label: '0-25%' },
      { value: '25-50', label: '25-50%' },
      { value: '50-75', label: '50-75%' },
      { value: '75-100', label: '75-100%' },
      { value: 'above', label: 'Выше уровня' },
      { value: 'na', label: 'Не предусмотрено', skipToQuestion: 30 },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 29,
    title: 'Состояние жидкости ГУР',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'fresh', label: 'Свежее' },
      { value: 'working', label: 'Рабочее' },
      { value: 'particles', label: 'С механическими примесями' },
      { value: 'water', label: 'Примеси воды / антифриза' },
      { value: 'burnt', label: 'Горелое' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 30,
    title: 'Уровень охлаждающей жидкости ДВС',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'below', label: 'Ниже уровня' },
      { value: 'level', label: 'Уровень' },
      { value: 'above', label: 'Выше уровня' },
      { value: 'na', label: 'Не предусмотрено', skipToQuestion: 34 },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 31,
    title: 'Цвет охлаждающей жидкости ДВС',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'red', label: 'Красный' },
      { value: 'green', label: 'Зеленый' },
      { value: 'blue', label: 'Синий' },
      { value: 'yellow', label: 'Желтый' },
      { value: 'clear', label: 'Бесцветный' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 32,
    title: 'Состояние охлаждающей жидкости ДВС',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'clean', label: 'Чистая' },
      { value: 'cloudy', label: 'Мутная' },
      { value: 'particles', label: 'Посторонние частицы' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 33,
    title: 'Температура кристаллизации ОЖ ДВС',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'less_25', label: 'Менее -25⁰С' },
      { value: '25_35', label: '-25 - 35⁰С' },
      { value: '35_45', label: '-35 - 45⁰С' },
      { value: 'more_45', label: 'Более -45⁰С' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 34,
    title: 'Уровень охлаждающей жидкости HV',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'below', label: 'Ниже уровня' },
      { value: 'level', label: 'Уровень' },
      { value: 'above', label: 'Выше уровня' },
      { value: 'na', label: 'Не предусмотрено', skipToQuestion: 38 },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 35,
    title: 'Цвет охлаждающей жидкости HV',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'red', label: 'Красный' },
      { value: 'green', label: 'Зеленый' },
      { value: 'blue', label: 'Синий' },
      { value: 'yellow', label: 'Желтый' },
      { value: 'clear', label: 'Бесцветный' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 36,
    title: 'Состояние охлаждающей жидкости HV',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'clean', label: 'Чистая' },
      { value: 'cloudy', label: 'Мутная' },
      { value: 'particles', label: 'Посторонние частицы' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 37,
    title: 'Температура кристаллизации ОЖ HV',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'less_25', label: 'Менее -25⁰С' },
      { value: '25_35', label: '-25 - 35⁰С' },
      { value: '35_45', label: '-35 - 45⁰С' },
      { value: 'more_45', label: 'Более -45⁰С' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 38,
    title: 'Уровень охлаждающей жидкости турбины',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'below', label: 'Ниже уровня' },
      { value: 'level', label: 'Уровень' },
      { value: 'above', label: 'Выше уровня' },
      { value: 'na', label: 'Не предусмотрено', skipToQuestion: 42 },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 39,
    title: 'Цвет охлаждающей жидкости турбины',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'red', label: 'Красный' },
      { value: 'green', label: 'Зеленый' },
      { value: 'blue', label: 'Синий' },
      { value: 'yellow', label: 'Желтый' },
      { value: 'clear', label: 'Бесцветный' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 40,
    title: 'Состояние охлаждающей жидкости турбины',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'clean', label: 'Чистая' },
      { value: 'cloudy', label: 'Мутная' },
      { value: 'particles', label: 'Посторонние частицы' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 41,
    title: 'Температура кристаллизации ОЖ турбины',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'less_25', label: 'Менее -25⁰С' },
      { value: '25_35', label: '-25 - 35⁰С' },
      { value: '35_45', label: '-35 - 45⁰С' },
      { value: 'more_45', label: 'Более -45⁰С' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 42,
    title: 'Уровень тормозной жидкости',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'below', label: 'Ниже уровня' },
      { value: 'level', label: 'Уровень' },
      { value: 'above', label: 'Выше уровня' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 43,
    title: 'Температура кипения тормозной жидкости',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'less_180', label: 'Менее 180⁰С' },
      { value: 'more_180', label: 'Более 180⁰С' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 44,
    title: 'Состояние тормозной жидкости',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'clean', label: 'Чистая' },
      { value: 'cloudy', label: 'Мутная' },
      { value: 'particles', label: 'Посторонние частицы' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 45,
    title: 'Уровень масла КПП',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'below', label: 'Ниже уровня' },
      { value: '0-25', label: '0-25%' },
      { value: '25-50', label: '25-50%' },
      { value: '50-75', label: '50-75%' },
      { value: '75-100', label: '75-100%' },
      { value: 'above', label: 'Выше уровня' },
      { value: 'need_disassembly', label: 'Требуется дополнительный разбор', skipToQuestion: 47 },
      { value: 'na', label: 'Не предусмотрено', skipToQuestion: 47 },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 46,
    title: 'Состояние масла КПП',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'fresh', label: 'Свежее' },
      { value: 'working', label: 'Рабочее' },
      { value: 'particles', label: 'С механическими примесями' },
      { value: 'burnt', label: 'Горелое' },
      { value: 'water', label: 'Примеси воды / антифриза' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 47,
    title: 'Омывающая жидкость',
    answerType: 'single',
    requiresPhoto: false,
    options: [
      { value: 'present', label: 'Присутствует' },
      { value: 'missing', label: 'Отсутствует' },
      { value: 'frozen', label: 'Замерзла' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 48,
    title: 'Работа стартера при запуске ДВС',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        requiresPhoto: false,
        subOptions: [
          { value: 'noise', label: 'Посторонний шум' },
          { value: 'long_start', label: 'Длительный запуск' },
          { value: 'jamming', label: 'Заклинивание' },
        ],
      },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 49,
    title: 'Работа ДВС',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'noise', label: 'Посторонний шум' },
          { value: 'uneven', label: 'Неровная работа' },
        ],
      },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 50,
    title: 'Работа КПП',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'noise', label: 'Посторонний шум' },
          { value: 'jolts', label: 'Пинки / Толчки' },
        ],
      },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 51,
    title: 'Течи технических жидкостей',
    answerType: 'single',
    options: [
      { value: 'no_leaks', label: 'Нет течей' },
      {
        value: 'has_leaks',
        label: 'Есть течи',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'valve_cover', label: 'Течь клапанной крышки' },
          { value: 'turbo', label: 'Течь турбокомпрессора' },
          { value: 'oil_cooler', label: 'Течь охладителя масла' },
          { value: 'brake_fluid', label: 'Течь тормозной жидкости' },
          { value: 'coolant', label: 'Течь антифриза' },
        ],
      },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 52,
    title: 'Состояние воздушного фильтра',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'dirty', label: 'Загрязнен' },
          { value: 'moisture', label: 'Попадание влаги' },
          { value: 'missing', label: 'Отсутствует' },
        ],
      },
      { value: 'need_disassembly', label: 'Требуется дополнительный разбор' },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 53,
    title: 'Состояние салонного фильтра',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'dirty', label: 'Загрязнен' },
          { value: 'moisture', label: 'Попадание влаги' },
          { value: 'missing', label: 'Отсутствует' },
        ],
      },
      { value: 'need_disassembly', label: 'Требуется дополнительный разбор' },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 54,
    title: 'Состояние фильтра ВВБ',
    answerType: 'single',
    options: [
      { value: 'ok', label: 'Исправно' },
      {
        value: 'bad',
        label: 'Неисправно',
        allowMultiple: true,
        requiresPhoto: false,
        subOptions: [
          { value: 'dirty', label: 'Загрязнен' },
          { value: 'moisture', label: 'Попадание влаги' },
          { value: 'missing', label: 'Отсутствует' },
        ],
      },
      { value: 'need_disassembly', label: 'Требуется дополнительный разбор' },
      { value: 'na', label: 'Не предусмотрено' },
      { value: 'other', label: 'Иное (указать текстом)', requiresText: true },
    ],
  },
  {
    id: 55,
    title: 'Иные замечания',
    answerType: 'single',
    options: [
      { value: 'add_notes', label: 'Добавить замечания (указать текстом)', requiresText: true },
      { value: 'complete', label: 'Завершить, замечаний нет' },
    ],
  },
];