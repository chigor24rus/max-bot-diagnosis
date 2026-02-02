import { useState, useEffect, useRef } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Avatar } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Icon from '@/components/ui/icon';
import DiagnosticHistory from '@/components/DiagnosticHistory';
import BotInfo from '@/components/BotInfo';

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
  timestamp: Date;
};

const Index = () => {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 0,
      type: 'bot',
      text: '👋 Привет! Я HEVSR Diagnostics bot — ваш помощник для проведения диагностики автомобилей.\n\nВведите команду /start чтобы начать или просто напишите мне!',
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
      const cleanNumber = text.toUpperCase().replace(/[^A-Z0-9]/g, '');
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

  const handleMechanicSelect = (selectedMechanic: string) => {
    setMechanic(selectedMechanic);
    setCurrentStep(2);
    addBotMessage(
      `✅ Отлично! Механик ${selectedMechanic} выбран.\n\nТеперь введите государственный номер автомобиля (в латинице).\n\nНапример: A159BK124`
    );
  };

  const handleDiagnosticTypeSelect = (type: string) => {
    setDiagnosticType(type);
    saveDiagnostic(type);
  };

  const handleSendMessage = () => {
    if (!inputValue.trim() || isLoading) return;
    
    const userText = inputValue.trim();
    addUserMessage(userText);
    setInputValue('');
    setIsLoading(true);
    
    processUserMessage(userText);
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
        `✅ Диагностика №${data.id} успешно сохранена!\n\n📋 Сводка:\n━━━━━━━━━━━━━━━━\n👤 Механик: ${mechanic}\n🚗 Госномер: ${carNumber}\n🛣 Пробег: ${parseInt(mileage).toLocaleString('ru-RU')} км\n🔧 Тип: ${typeLabel}\n━━━━━━━━━━━━━━━━\n\nВы можете скачать PDF отчёт или начать новую диагностику.`,
        ['Скачать PDF отчёт', 'Начать новую диагностику']
      );

      toast({
        title: '✅ Успешно!',
        description: `Диагностика №${data.id} сохранена`
      });
    } catch (error) {
      addBotMessage('❌ Произошла ошибка при сохранении. Попробуйте ещё раз или введите /cancel для отмены.', ['Начать новую диагностику']);
      
      toast({
        title: 'Ошибка',
        description: 'Не удалось сохранить диагностику',
        variant: 'destructive'
      });
      setIsLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!diagnosticId) return;
    
    setIsLoading(true);
    addBotMessage('📄 Генерирую PDF отчёт для печати...');

    try {
      const response = await fetch(`https://functions.poehali.dev/65879cb6-37f7-4a96-9bdc-04cfe5915ba6?id=${diagnosticId}`);
      
      if (!response.ok) {
        throw new Error('Ошибка генерации');
      }
      
      const data = await response.json();
      window.open(data.pdfUrl, '_blank');
      
      addBotMessage('✅ PDF отчёт готов и открыт в новой вкладке!\n\nМожете его распечатать для клиента.', ['Начать новую диагностику']);

      toast({
        title: '✅ Готово!',
        description: 'PDF отчёт открыт в новой вкладке'
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
    setCurrentStep(0);
    setMechanic('');
    setCarNumber('');
    setMileage('');
    setDiagnosticType('');
    setDiagnosticId(null);
    setInputValue('');
    setIsLoading(false);
    setActiveTab('chat');
    addBotMessage('🔄 Начинаем заново!\n\nВведите /start для новой диагностики.', ['Начать диагностику']);
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center p-2 sm:p-4">
      <Card className="w-full max-w-4xl h-[95vh] flex flex-col shadow-2xl border-2 border-primary/20 bg-slate-950/90 backdrop-blur overflow-hidden">
        
        <div className="bg-gradient-to-r from-primary via-primary to-accent p-4 sm:p-5 flex items-center gap-3 sm:gap-4 shadow-lg">
          <Avatar className="w-12 h-12 sm:w-14 sm:h-14 bg-white/10 backdrop-blur border-2 border-white/20">
            <div className="w-full h-full flex items-center justify-center">
              <Icon name="Bot" size={28} className="text-white" />
            </div>
          </Avatar>
          <div className="flex-1">
            <h1 className="text-xl sm:text-2xl font-bold text-white">HEVSR Diagnostics bot</h1>
            <div className="flex items-center gap-2 text-sm text-white/80">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span>онлайн</span>
            </div>
          </div>
        </div>
        
        <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col overflow-hidden">
          <TabsList className="w-full rounded-none bg-slate-900/50 border-b border-slate-700 p-0 h-auto">
            <TabsTrigger 
              value="chat" 
              className="flex-1 rounded-none data-[state=active]:bg-primary/10 data-[state=active]:text-primary py-3"
            >
              <Icon name="MessageSquare" size={16} className="mr-2" />
              Чат
            </TabsTrigger>
            <TabsTrigger 
              value="history" 
              className="flex-1 rounded-none data-[state=active]:bg-primary/10 data-[state=active]:text-primary py-3"
            >
              <Icon name="History" size={16} className="mr-2" />
              История
            </TabsTrigger>
            <TabsTrigger 
              value="info" 
              className="flex-1 rounded-none data-[state=active]:bg-primary/10 data-[state=active]:text-primary py-3"
            >
              <Icon name="Info" size={16} className="mr-2" />
              О боте
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="chat" className="flex-1 flex flex-col overflow-hidden m-0">
            <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-3 sm:space-y-4 bg-slate-900/30">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex gap-2 sm:gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'} animate-fade-in`}
                >
                  <Avatar className={`w-8 h-8 sm:w-10 sm:h-10 flex-shrink-0 ${
                    message.type === 'user' 
                      ? 'bg-primary' 
                      : 'bg-gradient-to-br from-accent to-primary'
                  }`}>
                    <div className="w-full h-full flex items-center justify-center">
                      <Icon 
                        name={message.type === 'user' ? 'User' : 'Bot'} 
                        size={message.type === 'user' ? 16 : 20} 
                        className="text-white" 
                      />
                    </div>
                  </Avatar>
                  
                  <div className={`flex flex-col max-w-[75%] sm:max-w-[70%] ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
                    <div
                      className={`rounded-2xl px-3 sm:px-4 py-2 sm:py-3 shadow-lg ${
                        message.type === 'user'
                          ? 'bg-primary text-white rounded-tr-sm'
                          : 'bg-slate-800 text-white border border-slate-700 rounded-tl-sm'
                      }`}
                    >
                      <p className="whitespace-pre-line leading-relaxed text-sm sm:text-base">{message.text}</p>
                      
                      {message.buttons && message.buttons.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {message.buttons.map((button, index) => (
                            <Button
                              key={index}
                              onClick={() => handleButtonClick(button)}
                              disabled={isLoading}
                              size="sm"
                              variant="outline"
                              className="bg-primary/10 hover:bg-primary/20 border-primary/40 text-white hover:text-white text-xs sm:text-sm"
                            >
                              {button}
                            </Button>
                          ))}
                        </div>
                      )}
                    </div>
                    <span className="text-xs text-slate-500 mt-1 px-1">
                      {formatTime(message.timestamp)}
                    </span>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex gap-3 animate-fade-in">
                  <Avatar className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-accent to-primary">
                    <div className="w-full h-full flex items-center justify-center">
                      <Icon name="Bot" size={20} className="text-white" />
                    </div>
                  </Avatar>
                  <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-4 py-3 shadow-lg">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            <div className="p-3 sm:p-4 bg-slate-900/80 border-t border-slate-700/50 backdrop-blur">
              <div className="flex gap-2">
                <Input
                  ref={inputRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Напишите сообщение..."
                  disabled={isLoading}
                  className="flex-1 bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 h-11 sm:h-12 text-sm sm:text-base focus:border-primary"
                  autoFocus
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || isLoading}
                  size="lg"
                  className="px-4 sm:px-6 h-11 sm:h-12"
                >
                  <Icon name="Send" size={20} />
                </Button>
              </div>
              <p className="text-xs text-slate-500 mt-2 text-center">
                Введите /help для списка команд
              </p>
            </div>
          </TabsContent>
          
          <TabsContent value="history" className="flex-1 overflow-y-auto p-3 sm:p-6 m-0 bg-slate-900/30">
            <DiagnosticHistory />
          </TabsContent>
          
          <TabsContent value="info" className="flex-1 overflow-y-auto p-3 sm:p-6 m-0 bg-slate-900/30">
            <BotInfo />
          </TabsContent>
        </Tabs>
      </Card>
    </div>
  );
};

export default Index;