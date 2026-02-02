import { useState, useEffect, useRef } from 'react';
import { useToast } from '@/hooks/use-toast';

export const mechanics = [
  'Подкорытов С.А.',
  'Костенко В.Ю.',
  'Иванюта Д.И.',
  'Загороднюк Н.Д.'
];

export const diagnosticTypes = [
  { value: '5min', label: '5-ти минутка' },
  { value: 'dhch', label: 'ДХЧ' },
  { value: 'des', label: 'ДЭС' }
];

export type Message = {
  id: number;
  type: 'bot' | 'user';
  text: string;
  buttons?: string[];
  timestamp: Date;
};

export const useChatLogic = () => {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      type: 'bot',
      text: '👋 Привет! Я HEVSR Diagnostics bot — ваш помощник для проведения диагностики автомобилей.\n\n✨ Теперь я работаю в MAX мессенджере!\nОткройте бота по ссылке: https://max.ru/id245900919213_bot\n\nИли введите команду /start чтобы начать здесь!',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [currentStep, setCurrentStep] = useState(0);
  const [mechanic, setMechanic] = useState('');
  const [carNumber, setCarNumber] = useState('');
  const [mileage, setMileage] = useState('');
  const [diagnosticType, setDiagnosticType] = useState('');
  const [diagnosticId, setDiagnosticId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addBotMessage = (text: string, buttons?: string[]) => {
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'bot',
        text,
        buttons,
        timestamp: new Date()
      }]);
      setIsLoading(false);
    }, 800);
  };

  const addUserMessage = (text: string) => {
    setMessages(prev => [...prev, {
      id: Date.now(),
      type: 'user',
      text,
      timestamp: new Date()
    }]);
  };

  const resetChat = () => {
    setCurrentStep(0);
    setMechanic('');
    setCarNumber('');
    setMileage('');
    setDiagnosticType('');
    setDiagnosticId(null);
    addBotMessage(
      'Чат сброшен! Введите /start чтобы начать новую диагностику.',
      ['Начать диагностику']
    );
  };

  const handleMechanicSelect = (selectedMechanic: string) => {
    setMechanic(selectedMechanic);
    setCurrentStep(2);
    addBotMessage(
      `✅ Отлично! Механик ${selectedMechanic} выбран.\n\nТеперь введите государственный номер автомобиля.\n\n⚠️ ВАЖНО: Используйте только латинские буквы (A-Z) и цифры!\nНапример: A159BK124 или B777CC777`
    );
  };

  const handleDiagnosticTypeSelect = (type: string) => {
    setDiagnosticType(type);
    saveDiagnostic(type);
  };

  const saveDiagnostic = async (type: string) => {
    setIsLoading(true);
    
    addBotMessage('⏳ Сохраняю данные диагностики в базу...');

    try {
      const response = await fetch('https://functions.poehali.dev/e76024e1-4735-4e57-bf5f-060276b574c8', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mechanic,
          carNumber,
          mileage: parseInt(mileage),
          diagnosticType: type
        })
      });
      
      if (!response.ok) {
        throw new Error('Ошибка при сохранении');
      }
      
      const data = await response.json();
      setDiagnosticId(data.id);
      setCurrentStep(5);
      
      const typeLabel = diagnosticTypes.find(d => d.value === type)?.label;
      
      addBotMessage(
        `✅ Диагностика успешно сохранена!\n\n📝 Информация:\n• Механик: ${mechanic}\n• Автомобиль: ${carNumber}\n• Пробег: ${parseInt(mileage).toLocaleString('ru-RU')} км\n• Тип: ${typeLabel}\n• ID записи: ${data.id}\n\nЧто дальше?`,
        ['Скачать PDF отчёт', 'Начать новую диагностику']
      );
    } catch (error) {
      addBotMessage(
        '❌ Произошла ошибка при сохранении диагностики.\n\nПопробуйте ещё раз или обратитесь к администратору.'
      );
      toast({
        title: 'Ошибка',
        description: 'Не удалось сохранить диагностику',
        variant: 'destructive'
      });
    }
  };

  const handleGenerateReport = async () => {
    if (!diagnosticId) {
      toast({
        title: 'Ошибка',
        description: 'ID диагностики не найден',
        variant: 'destructive'
      });
      return;
    }

    setIsLoading(true);
    addBotMessage('⏳ Генерирую PDF отчёт...');

    try {
      const response = await fetch(`https://functions.poehali.dev/0cb6b5be-e5ab-45d5-8cec-fd15b07ba1e5?id=${diagnosticId}`);
      
      if (!response.ok) {
        throw new Error('Ошибка генерации PDF');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `diagnostic_${diagnosticId}_${Date.now()}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      addBotMessage(
        '✅ PDF отчёт успешно сформирован и загружен!\n\nЧто дальше?',
        ['Начать новую диагностику']
      );
      
      toast({
        title: 'Успешно!',
        description: 'PDF отчёт загружен'
      });
    } catch (error) {
      addBotMessage(
        '❌ Произошла ошибка при генерации PDF.\n\nПопробуйте ещё раз или обратитесь к администратору.'
      );
      toast({
        title: 'Ошибка',
        description: 'Не удалось сгенерировать PDF',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const processUserMessage = (text: string) => {
    const lowerText = text.toLowerCase().trim();
    
    if (lowerText === '/start' || lowerText.includes('начать') || lowerText.includes('осмотр')) {
      setCurrentStep(1);
      addBotMessage('Отлично! Выберите механика, который проводит диагностику:', mechanics);
    }
    else if (lowerText === '/help' || lowerText.includes('помощь') || lowerText.includes('команды')) {
      addBotMessage(
        '📋 Доступные команды:\n\n/start - Начать диагностику\n/help - Показать помощь\n/history - История диагностик\n/info - О боте\n/cancel - Отменить текущую операцию\n\nПросто напишите что нужно, и я постараюсь помочь!'
      );
    }
    else if (lowerText === '/history' || lowerText.includes('история')) {
      setActiveTab('history');
      addBotMessage('📊 Открываю историю диагностик...');
    }
    else if (lowerText === '/info' || lowerText.includes('информация') || lowerText.includes('о боте')) {
      setActiveTab('info');
      addBotMessage('ℹ️ Открываю информацию о боте...');
    }
    else if (lowerText === '/cancel' || lowerText.includes('отмена')) {
      resetChat();
      addBotMessage('✅ Операция отменена. Введите /start для начала новой диагностики.');
    }
    else if (currentStep === 0) {
      addBotMessage(
        `Я понял, что вы написали: "${text}"\n\nЧтобы начать диагностику автомобиля, введите команду /start или нажмите кнопку ниже:`,
        ['Начать диагностику']
      );
    }
    else if (currentStep === 1 && mechanics.some(m => m.toLowerCase().includes(lowerText))) {
      const foundMechanic = mechanics.find(m => m.toLowerCase().includes(lowerText));
      if (foundMechanic) {
        handleMechanicSelect(foundMechanic);
      }
    }
    else if (currentStep === 2) {
      const hasCyrillic = /[А-Яа-яЁё]/.test(text);
      if (hasCyrillic) {
        addBotMessage(
          '❌ Обнаружены русские буквы!\n\n⚠️ Госномер должен быть введён ТОЛЬКО латинскими буквами (A-Z).\n\nНапример:\n✅ A159BK124 (правильно)\n❌ А159ВК124 (неправильно - русские буквы)\n\nПопробуйте ещё раз:'
        );
        return;
      }
      
      const cleanNumber = text.toUpperCase().replace(/[^A-Z0-9]/g, '');
      if (!/^[A-Z0-9]+$/.test(cleanNumber)) {
        addBotMessage(
          '⚠️ Используйте только латинские буквы (A-Z) и цифры!\n\nНапример: A159BK124'
        );
        return;
      }
      
      if (cleanNumber.length >= 5) {
        setCarNumber(cleanNumber);
        setCurrentStep(3);
        addBotMessage(
          `✅ Госномер ${cleanNumber} принят!\n\nТеперь введите текущий пробег автомобиля (в километрах).`
        );
      } else {
        addBotMessage(
          '⚠️ Госномер должен содержать минимум 5 символов (буквы и цифры).\n\nПопробуйте ещё раз, например: A159BK124'
        );
      }
    }
    else if (currentStep === 3) {
      const mileageNum = text.replace(/\D/g, '');
      if (mileageNum && parseInt(mileageNum) > 0) {
        setMileage(mileageNum);
        setCurrentStep(4);
        addBotMessage(
          `✅ Пробег ${parseInt(mileageNum).toLocaleString('ru-RU')} км принят!\n\nТеперь выберите тип диагностики:`,
          diagnosticTypes.map(d => d.label)
        );
      } else {
        addBotMessage(
          '⚠️ Пожалуйста, введите пробег цифрами.\n\nНапример: 150000'
        );
      }
    }
    else if (currentStep === 4) {
      const selectedType = diagnosticTypes.find(d => 
        d.label.toLowerCase().includes(lowerText) || lowerText.includes(d.value)
      );
      if (selectedType) {
        handleDiagnosticTypeSelect(selectedType.value);
      } else {
        addBotMessage(
          '⚠️ Пожалуйста, выберите один из типов диагностики:',
          diagnosticTypes.map(d => d.label)
        );
      }
    }
    else {
      addBotMessage(
        'Извините, не совсем понял. Используйте /help для списка команд.'
      );
    }
  };

  const handleButtonClick = (buttonText: string) => {
    if (isLoading) return;
    
    addUserMessage(buttonText);
    setIsLoading(true);

    if (buttonText === 'Начать диагностику' || buttonText === 'Начать осмотр автомобиля') {
      setCurrentStep(1);
      addBotMessage('Отлично! Выберите механика, который проводит диагностику:', mechanics);
    } 
    else if (mechanics.includes(buttonText)) {
      handleMechanicSelect(buttonText);
    } 
    else if (diagnosticTypes.map(d => d.label).includes(buttonText)) {
      const selectedType = diagnosticTypes.find(d => d.label === buttonText);
      if (selectedType) {
        handleDiagnosticTypeSelect(selectedType.value);
      }
    } 
    else if (buttonText === 'Скачать PDF отчёт') {
      handleGenerateReport();
    } 
    else if (buttonText === 'Начать новую диагностику') {
      resetChat();
    }
  };

  const handleSendMessage = () => {
    if (!inputValue.trim() || isLoading) return;
    
    const userText = inputValue.trim();
    addUserMessage(userText);
    setInputValue('');
    setIsLoading(true);
    
    processUserMessage(userText);
  };

  return {
    activeTab,
    setActiveTab,
    messages,
    inputValue,
    setInputValue,
    isLoading,
    messagesEndRef,
    inputRef,
    handleButtonClick,
    handleSendMessage
  };
};
