import { Section } from '@/types/diagnostic';

export const dhchSections: Section[] = [
  {
    id: 'general',
    title: 'Общий раздел',
    questions: [
      {
        id: 'engine_oil_level',
        text: 'Уровень масла ДВС',
        type: 'choice',
        options: [
          'Ниже уровня',
          '0-25%',
          '25-50%',
          '50-75%',
          '75-100%',
          'Выше уровня',
          'Не предусмотренно',
          'Иное (указать текстом)'
        ],
        allowText: true,
        allowPhoto: true
      },
      {
        id: 'power_steering_fluid_level',
        text: 'Уровень жидкости ГУР',
        type: 'choice',
        options: [
          'Ниже уровня',
          '0-25%',
          '25-50%',
          '50-75%',
          '75-100%',
          'Выше уровня',
          'Не предусмотренно',
          'Иное (указать текстом)'
        ],
        allowText: true,
        allowPhoto: true
      },
      {
        id: 'coolant_engine_level',
        text: 'Уровень охлаждающей жидкости ДВС',
        type: 'choice',
        options: [
          'Ниже уровня',
          'Уровень',
          'Выше уровня',
          'Не предусмотренно',
          'Иное (указать текстом)'
        ],
        allowText: true,
        allowPhoto: true
      },
      {
        id: 'coolant_hv_level',
        text: 'Уровень охлаждающей жидкости HV',
        type: 'choice',
        options: [
          'Ниже уровня',
          'Уровень',
          'Выше уровня',
          'Не предусмотренно',
          'Иное (указать текстом)'
        ],
        allowText: true,
        allowPhoto: true
      },
      {
        id: 'coolant_turbo_level',
        text: 'Уровень охлаждающей жидкости турбины',
        type: 'choice',
        options: [
          'Ниже уровня',
          'Уровень',
          'Выше уровня',
          'Не предусмотренно',
          'Иное (указать текстом)'
        ],
        allowText: true,
        allowPhoto: true
      },
      {
        id: 'brake_fluid_level',
        text: 'Уровень тормозной жидкости',
        type: 'choice',
        options: [
          'Ниже уровня',
          'Уровень',
          'Выше уровня',
          'Иное (указать текстом)'
        ],
        allowText: true,
        allowPhoto: true
      },
      {
        id: 'drive_type',
        text: 'Укажите привод автомобиля',
        type: 'choice',
        options: [
          'Передний',
          'Задний',
          'Полный'
        ],
        allowPhoto: false
      }
    ]
  },
  {
    id: 'fwd',
    title: 'Переднеприводные автомобили',
    questions: [
      {
        id: 'fwd_placeholder_1',
        text: 'Вопрос 1 (переднеприводные) - ожидается данные от пользователя',
        type: 'choice',
        options: ['Исправно', 'Неисправно']
      }
    ],
    conditional: {
      dependsOn: 'drive_type',
      value: 'Передний'
    }
  },
  {
    id: 'rwd',
    title: 'Заднеприводные автомобили',
    questions: [
      {
        id: 'rwd_placeholder_1',
        text: 'Вопрос 1 (заднеприводные) - ожидается данные от пользователя',
        type: 'choice',
        options: ['Исправно', 'Неисправно']
      }
    ],
    conditional: {
      dependsOn: 'drive_type',
      value: 'Задний'
    }
  },
  {
    id: 'awd',
    title: 'Полноприводные автомобили',
    questions: [
      {
        id: 'awd_placeholder_1',
        text: 'Вопрос 1 (полноприводные) - ожидается данные от пользователя',
        type: 'choice',
        options: ['Исправно', 'Неисправно']
      }
    ],
    conditional: {
      dependsOn: 'drive_type',
      value: 'Полный'
    }
  }
];