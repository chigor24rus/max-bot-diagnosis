import { useState } from 'react';
import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Progress } from '@/components/ui/progress';
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

const Index = () => {
  const { toast } = useToast();
  const [step, setStep] = useState(0);
  const [mechanic, setMechanic] = useState('');
  const [carNumber, setCarNumber] = useState('');
  const [mileage, setMileage] = useState('');
  const [diagnosticType, setDiagnosticType] = useState('');
  const [diagnosticId, setDiagnosticId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const progress = (step / 5) * 100;

  const handleStart = () => {
    setStep(1);
  };

  const handleMechanicSelect = (selectedMechanic: string) => {
    setMechanic(selectedMechanic);
    setStep(2);
  };

  const handleCarNumberSubmit = () => {
    if (carNumber.trim()) {
      setStep(3);
    }
  };

  const handleMileageSubmit = () => {
    if (mileage.trim() && /^\d+$/.test(mileage)) {
      setStep(4);
    }
  };

  const handleDiagnosticTypeSelect = async (type: string) => {
    setDiagnosticType(type);
    setIsLoading(true);
    
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
        throw new Error('Ошибка при сохранении диагностики');
      }
      
      const data = await response.json();
      setDiagnosticId(data.id);
      setStep(5);
      
      toast({
        title: 'Успешно!',
        description: 'Диагностика сохранена в базу данных'
      });
    } catch (error) {
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
    try {
      const response = await fetch(`https://functions.poehali.dev/65879cb6-37f7-4a96-9bdc-04cfe5915ba6?id=${diagnosticId}`);
      
      if (!response.ok) {
        throw new Error('Ошибка при генерации отчёта');
      }
      
      const data = await response.json();
      window.open(data.pdfUrl, '_blank');
      
      toast({
        title: 'Готово!',
        description: 'PDF отчёт успешно сгенерирован'
      });
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось создать отчёт',
        variant: 'destructive'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-muted/30 to-background flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {step > 0 && (
          <div className="mb-6 animate-fade-in">
            <Progress value={progress} className="h-2" />
            <p className="text-sm text-muted-foreground mt-2 text-center">
              Шаг {step} из 5
            </p>
          </div>
        )}

        {step === 0 && (
          <Card className="shadow-2xl border-2 animate-scale-in">
            <CardHeader className="text-center pb-4">
              <div className="mx-auto mb-4 w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
                <Icon name="Car" size={40} className="text-primary" />
              </div>
              <CardTitle className="text-4xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                Бот МАХ
              </CardTitle>
              <CardDescription className="text-lg mt-2">
                Система диагностики автомобилей
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-muted/50 p-4 rounded-lg">
                <p className="text-center text-foreground">
                  Добро пожаловать в систему диагностики автосервиса!
                  <br />
                  Нажмите кнопку ниже, чтобы начать осмотр автомобиля.
                </p>
              </div>
              <Button 
                onClick={handleStart} 
                size="lg" 
                className="w-full text-lg h-14 shadow-lg hover:shadow-xl transition-all"
              >
                <Icon name="ClipboardCheck" className="mr-2" size={24} />
                Начать осмотр автомобиля
              </Button>
            </CardContent>
          </Card>
        )}

        {step === 1 && (
          <Card className="shadow-2xl border-2 animate-fade-in">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Icon name="UserCheck" size={24} className="text-primary" />
                </div>
                <CardTitle className="text-2xl">Выбор автомеханика</CardTitle>
              </div>
              <CardDescription>
                Выберите, кто проводит диагностику автомобиля
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {mechanics.map((mech) => (
                <Button
                  key={mech}
                  onClick={() => handleMechanicSelect(mech)}
                  variant="outline"
                  className="w-full justify-start text-left h-auto py-4 hover:bg-primary/5 hover:border-primary transition-all"
                >
                  <Icon name="User" className="mr-3" size={20} />
                  <span className="text-lg">{mech}</span>
                </Button>
              ))}
            </CardContent>
          </Card>
        )}

        {step === 2 && (
          <Card className="shadow-2xl border-2 animate-fade-in">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Icon name="Hash" size={24} className="text-primary" />
                </div>
                <CardTitle className="text-2xl">Госномер автомобиля</CardTitle>
              </div>
              <CardDescription>
                Введите государственный номер в латинице
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-muted/30 p-4 rounded-lg border">
                <p className="text-sm text-muted-foreground mb-2">Выбран механик:</p>
                <p className="font-semibold text-lg flex items-center gap-2">
                  <Icon name="CheckCircle2" size={20} className="text-primary" />
                  {mechanic}
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="carNumber" className="text-base">
                  Госномер (например: A159BK124)
                </Label>
                <Input
                  id="carNumber"
                  value={carNumber}
                  onChange={(e) => setCarNumber(e.target.value.toUpperCase())}
                  placeholder="A159BK124"
                  className="text-lg h-12"
                />
              </div>
              <Button 
                onClick={handleCarNumberSubmit}
                disabled={!carNumber.trim()}
                size="lg" 
                className="w-full text-lg h-12"
              >
                Продолжить
                <Icon name="ArrowRight" className="ml-2" size={20} />
              </Button>
            </CardContent>
          </Card>
        )}

        {step === 3 && (
          <Card className="shadow-2xl border-2 animate-fade-in">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Icon name="Gauge" size={24} className="text-primary" />
                </div>
                <CardTitle className="text-2xl">Пробег автомобиля</CardTitle>
              </div>
              <CardDescription>
                Введите текущий пробег автомобиля в километрах
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-muted/30 p-4 rounded-lg border space-y-2">
                <div>
                  <p className="text-sm text-muted-foreground">Механик:</p>
                  <p className="font-semibold">{mechanic}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Госномер:</p>
                  <p className="font-semibold text-lg">{carNumber}</p>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="mileage" className="text-base">
                  Пробег (только цифры)
                </Label>
                <Input
                  id="mileage"
                  type="text"
                  value={mileage}
                  onChange={(e) => {
                    const value = e.target.value.replace(/\D/g, '');
                    setMileage(value);
                  }}
                  placeholder="150000"
                  className="text-lg h-12"
                />
                {mileage && (
                  <p className="text-sm text-muted-foreground">
                    {parseInt(mileage).toLocaleString('ru-RU')} км
                  </p>
                )}
              </div>
              <Button 
                onClick={handleMileageSubmit}
                disabled={!mileage.trim() || !/^\d+$/.test(mileage)}
                size="lg" 
                className="w-full text-lg h-12"
              >
                Продолжить
                <Icon name="ArrowRight" className="ml-2" size={20} />
              </Button>
            </CardContent>
          </Card>
        )}

        {step === 4 && (
          <Card className="shadow-2xl border-2 animate-fade-in">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
                  <Icon name="Wrench" size={24} className="text-primary" />
                </div>
                <CardTitle className="text-2xl">Тип диагностики</CardTitle>
              </div>
              <CardDescription>
                Выберите тип диагностики для проведения осмотра
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-muted/30 p-4 rounded-lg border space-y-2">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Механик:</p>
                    <p className="font-semibold">{mechanic}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Госномер:</p>
                    <p className="font-semibold">{carNumber}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-muted-foreground">Пробег:</p>
                    <p className="font-semibold">{parseInt(mileage).toLocaleString('ru-RU')} км</p>
                  </div>
                </div>
              </div>
              <RadioGroup value={diagnosticType} onValueChange={handleDiagnosticTypeSelect}>
                <div className="space-y-3">
                  {diagnosticTypes.map((type) => (
                    <Label
                      key={type.value}
                      htmlFor={type.value}
                      className="flex items-center space-x-3 border-2 rounded-lg p-4 cursor-pointer hover:bg-primary/5 hover:border-primary transition-all"
                    >
                      <RadioGroupItem value={type.value} id={type.value} />
                      <span className="text-lg font-medium">{type.label}</span>
                    </Label>
                  ))}
                </div>
              </RadioGroup>
            </CardContent>
          </Card>
        )}

        {step === 5 && (
          <Card className="shadow-2xl border-2 animate-scale-in">
            <CardHeader className="text-center">
              <div className="mx-auto mb-4 w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center">
                <Icon name="CheckCircle2" size={48} className="text-primary" />
              </div>
              <CardTitle className="text-3xl">Данные приняты!</CardTitle>
              <CardDescription className="text-base mt-2">
                Информация о диагностике успешно сохранена
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-gradient-to-br from-primary/5 to-accent/5 p-6 rounded-lg border-2 space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground font-medium">Механик</p>
                    <p className="font-bold text-lg">{mechanic}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground font-medium">Госномер</p>
                    <p className="font-bold text-lg">{carNumber}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground font-medium">Пробег</p>
                    <p className="font-bold text-lg">{parseInt(mileage).toLocaleString('ru-RU')} км</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground font-medium">Тип диагностики</p>
                    <p className="font-bold text-lg">
                      {diagnosticTypes.find(t => t.value === diagnosticType)?.label}
                    </p>
                  </div>
                </div>
              </div>
              <div className="space-y-3">
                <Button 
                  onClick={handleGenerateReport}
                  disabled={isLoading || !diagnosticId}
                  size="lg" 
                  variant="default"
                  className="w-full text-lg h-12"
                >
                  <Icon name="FileText" className="mr-2" size={20} />
                  {isLoading ? 'Генерация...' : 'Скачать PDF отчёт'}
                </Button>
                <Button 
                  onClick={() => {
                    setStep(0);
                    setMechanic('');
                    setCarNumber('');
                    setMileage('');
                    setDiagnosticType('');
                    setDiagnosticId(null);
                  }}
                  size="lg"
                  variant="outline" 
                  className="w-full text-lg h-12"
                >
                  <Icon name="Plus" className="mr-2" size={20} />
                  Начать новую диагностику
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default Index;