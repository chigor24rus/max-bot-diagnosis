import { Section } from '@/types/diagnostic';

export const priemkaSections: Section[] = [
  {
    id: 'general',
    title: 'Общий раздел',
    questions: [
      {
        id: 'placeholder_1',
        text: 'Вопрос 1 - ожидается данные от пользователя',
        type: 'choice',
        options: ['Исправно', 'Неисправно']
      }
    ]
  }
];
