import { Section } from '@/types/diagnostic';

export const dhchSections: Section[] = [
  {
    id: 'general',
    title: 'Общий раздел',
    questions: [
      {
        id: 'general_placeholder_1',
        text: 'Вопрос 1 (общий раздел) - ожидается данные от пользователя',
        type: 'choice',
        options: ['Исправно', 'Неисправно']
      },
      {
        id: 'general_placeholder_2',
        text: 'Вопрос 2 (общий раздел) - ожидается данные от пользователя',
        type: 'choice',
        options: ['Исправно', 'Неисправно']
      },
      {
        id: 'drive_type',
        text: 'Тип привода автомобиля',
        type: 'choice',
        options: [
          'Переднеприводный',
          'Заднеприводный', 
          'Полноприводный'
        ]
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
      value: 'Переднеприводный'
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
      value: 'Заднеприводный'
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
      value: 'Полноприводный'
    }
  }
];
