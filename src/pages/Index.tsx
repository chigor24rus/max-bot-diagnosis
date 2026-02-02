import { useState, useEffect, useRef } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import Icon from '@/components/ui/icon';

const mechanics = [
  'Подкорытов С.А.',
  'Костенко В.Ю.',
  'Иванюта Д.И.',
  'Загороднюк Н.Д.'
];

const diagnosticTypes = [
  { value: '5min', label: '5-ти минутка' },
  { value: 'dhch', label: 'ДХЧ' },
  { value: 'des', label: 'ДЭС' }
];

type Message = {
  id: number;
  type: 'bot' | 'user';
  text: string;
  buttons?: string[];
  isInput?: boolean;
  inputType?: 'text' | 'number';
  inputPlaceholder?: string;
};

const Index = () => {
  const { toast } = useToast();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      type: 'bot',
      text: '👋 Привет! Я бот МАХ — ваш помощник для проведения диагностики автомобилей.\n\nНажмите кнопку ниже, чтобы начать осмотр.',
      buttons: ['Начать осмотр автомобиля']
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
  const [waitingForInput, setWaitingForInput] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addBotMessage = (text: string, buttons?: string[], isInput = false, inputType?: 'text' | 'number', inputPlaceholder?: string) => {
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: prev.length,
        type: 'bot',
        text,
        buttons,
        isInput,
        inputType,
        inputPlaceholder
      }]);
      if (isInput) {
        setWaitingForInput(true);
      }
    }, 500);
  };

  const addUserMessage = (text: string) => {
    setMessages(prev => [...prev, {
      id: prev.length,
      type: 'user',
      text
    }]);
  };

  const handleButtonClick = (buttonText: string) => {
    if (isLoading) return;
    
    addUserMessage(buttonText);

    if (buttonText === 'Начать осмотр автомобиля') {
      setCurrentStep(1);
      addBotMessage('Выберите механика, который проводит диагностику:', mechanics);
    } else if (mechanics.includes(buttonText)) {
      setMechanic(buttonText);
      setCurrentStep(2);
      addBotMessage(
        'Отлично! Теперь введите государственный номер автомобиля в латинице.\n\nНапример: A159BK124',
        undefined,
        true,
        'text',
        'A159BK124'
      );
    } else if (diagnosticTypes.map(d => d.label).includes(buttonText)) {
      const selectedType = diagnosticTypes.find(d => d.label === buttonText);
      if (selectedType) {
        setDiagnosticType(selectedType.value);
        saveDiagnostic(selectedType.value);
      }
    } else if (buttonText === 'Скачать PDF отчёт') {
      handleGenerateReport();
    } else if (buttonText === 'Начать новую диагностику') {
      resetChat();
    }
  };

  const handleInputSubmit = () => {
    if (!inputValue.trim() || isLoading) return;
    
    setWaitingForInput(false);
    addUserMessage(inputValue);

    if (currentStep === 2) {
      setCarNumber(inputValue.toUpperCase());
      setCurrentStep(3);
      addBotMessage(
        'Принято! Теперь введите текущий пробег автомобиля (только цифры).\n\nНапример: 150000',
        undefined,
        true,
        'number',
        '150000'
      );
    } else if (currentStep === 3) {
      if (!/^\d+$/.test(inputValue)) {
        addBotMessage('⚠️ Пожалуйста, введите только цифры для пробега.', undefined, true, 'number', '150000');
        return;
      }
      setMileage(inputValue);
      setCurrentStep(4);
      addBotMessage(
        'Отлично! Теперь выберите тип диагностики:',
        diagnosticTypes.map(d => d.label)
      );
    }

    setInputValue('');
  };

  const saveDiagnostic = async (type: string) => {
    setIsLoading(true);
    
    addBotMessage('⏳ Сохраняю данные диагностики...');

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
        `✅ Диагностика успешно сохранена!\n\n📋 Данные:\n• Механик: ${mechanic}\n• Госномер: ${carNumber}\n• Пробег: ${parseInt(mileage).toLocaleString('ru-RU')} км\n• Тип: ${typeLabel}\n\nВы можете скачать PDF отчёт или начать новую диагностику.`,
        ['Скачать PDF отчёт', 'Начать новую диагностику']
      );

      toast({
        title: 'Успешно!',
        description: 'Диагностика сохранена в базу данных'
      });
    } catch (error) {
      addBotMessage('❌ Произошла ошибка при сохранении диагностики. Попробуйте ещё раз.', ['Начать новую диагностику']);
      
      toast({
        title: 'Ошибка',
        description: 'Не удалось сохранить диагностику',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!diagnosticId) return;
    
    setIsLoading(true);
    addBotMessage('📄 Генерирую PDF отчёт...');

    try {
      const response = await fetch(`https://functions.poehali.dev/65879cb6-37f7-4a96-9bdc-04cfe5915ba6?id=${diagnosticId}`);
      
      if (!response.ok) {
        throw new Error('Ошибка генерации');
      }
      
      const data = await response.json();
      window.open(data.pdfUrl, '_blank');
      
      addBotMessage('✅ PDF отчёт готов и открыт в новой вкладке!', ['Начать новую диагностику']);

      toast({
        title: 'Готово!',
        description: 'PDF отчёт успешно сгенерирован'
      });
    } catch (error) {
      addBotMessage('❌ Не удалось создать отчёт. Попробуйте ещё раз.', ['Скачать PDF отчёт', 'Начать новую диагностику']);
      
      toast({
        title: 'Ошибка',
        description: 'Не удалось создать отчёт',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const resetChat = () => {
    setMessages([
      {
        id: 0,
        type: 'bot',
        text: '👋 Начинаем новую диагностику!\n\nНажмите кнопку ниже, чтобы начать.',
        buttons: ['Начать осмотр автомобиля']
      }
    ]);
    setCurrentStep(0);
    setMechanic('');
    setCarNumber('');
    setMileage('');
    setDiagnosticType('');
    setDiagnosticId(null);
    setInputValue('');
    setWaitingForInput(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-4">
      <Card className="w-full max-w-3xl h-[85vh] flex flex-col shadow-2xl border-2 border-primary/20 bg-slate-950/90 backdrop-blur">
        <div className="bg-gradient-to-r from-primary to-accent p-5 flex items-center gap-4 rounded-t-lg">
          <div className="w-14 h-14 bg-white/10 backdrop-blur rounded-full flex items-center justify-center">
            <Icon name="Bot" size={32} className="text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">Бот МАХ</h1>
            <p className="text-sm text-white/80">Диагностика автомобилей</p>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                  message.type === 'user'
                    ? 'bg-primary text-white'
                    : 'bg-slate-800 text-white border border-slate-700'
                }`}
              >
                <p className="whitespace-pre-line leading-relaxed">{message.text}</p>
                
                {message.buttons && (
                  <div className="flex flex-wrap gap-2 mt-4">
                    {message.buttons.map((button, index) => (
                      <Button
                        key={index}
                        onClick={() => handleButtonClick(button)}
                        disabled={isLoading}
                        variant={message.type === 'user' ? 'secondary' : 'outline'}
                        className="bg-primary/10 hover:bg-primary/20 border-primary/30 text-white"
                      >
                        {button}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start animate-fade-in">
              <div className="bg-slate-800 border border-slate-700 rounded-2xl px-5 py-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse"></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {waitingForInput && (
          <div className="p-4 bg-slate-900/50 border-t border-slate-700">
            <div className="flex gap-2">
              <Input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleInputSubmit()}
                placeholder="Введите ответ..."
                disabled={isLoading}
                className="flex-1 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 h-12"
                autoFocus
              />
              <Button
                onClick={handleInputSubmit}
                disabled={!inputValue.trim() || isLoading}
                size="lg"
                className="px-6"
              >
                <Icon name="Send" size={20} />
              </Button>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
};

export default Index;
