import { Section } from '@/types/diagnostic';

export const priemkaSections: Section[] = [
  {
    id: 'photos',
    title: 'Фотофиксация автомобиля',
    questions: [
      {
        id: 'photo_license_plate',
        text: 'Фото номерного знака автомобиля',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_front',
        text: 'Фото всей передней части автомобиля',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_windshield',
        text: 'Фото лобового стекла',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_front_left_fender',
        text: 'Фото переднее левое крыло',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_front_left_door',
        text: 'Фото передняя левая дверь',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_rear_left_door',
        text: 'Фото задняя левая дверь',
        type: 'choice',
        options: ['Назад', 'Не предусмотрено'],
        allowPhoto: true
      },
      {
        id: 'photo_rear_left_fender',
        text: 'Фото заднее левое крыло',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_rear',
        text: 'Фото всей задней части автомобиля',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_rear_right_fender',
        text: 'Фото заднее правое крыло',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_rear_right_door',
        text: 'Фото задняя правая дверь',
        type: 'choice',
        options: ['Назад', 'Не предусмотрено'],
        allowPhoto: true
      },
      {
        id: 'photo_front_right_door',
        text: 'Фото передняя правая дверь',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_front_right_fender',
        text: 'Фото переднее правое крыло',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_roof',
        text: 'Фото крыши автомобиля',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_damaged_elements',
        text: 'Фото наружних повреждённых элементов крупно',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_driver_door_card',
        text: 'Фото дверной карты водительской двери',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_driver_seat',
        text: 'Фото водительского сиденья, включая ножной коврик',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_passenger_seat',
        text: 'Фото переднего пассажирского сиденья, включая ножной коврик',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_dashboard',
        text: 'Фото панели приборов при заведённом автомобиле, наличие горящих лампы неисправностей',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_odometer',
        text: 'Фото показаний одометра (Общий пробег)',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_keys',
        text: 'Фото ключей со всех сторон',
        type: 'photo',
        allowPhoto: true
      },
      {
        id: 'photo_additional',
        text: 'Дополнительные фото при необходимости',
        type: 'choice',
        options: ['Назад', 'Доп. Фото нет'],
        allowPhoto: true
      },
      {
        id: 'other_notes',
        text: 'Иные замечания',
        type: 'choice',
        options: ['Добавить замечания (указать текстом)', 'Завершить, замечаний нет', 'Назад'],
        allowText: true
      }
    ]
  }
];