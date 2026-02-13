import { useState, useMemo, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';
import { priemkaSections } from '@/data/priemka-checklist';
import { DiagnosticData, DiagnosticAnswer, Section } from '@/types/diagnostic';

interface DiagnosticPriemkaProps {
  onComplete: (data: DiagnosticData) => void;
  onCancel: () => void;
}

type Mechanic = {
  id: number;
  name: string;
};

const DiagnosticPriemka = ({ onComplete, onCancel }: DiagnosticPriemkaProps) => {
  const { toast } = useToast();
  const [step, setStep] = useState<'mechanic' | 'carInfo' | 'diagnostic'>('mechanic');
  const [mechanics, setMechanics] = useState<Mechanic[]>([]);
  const [loadingMechanics, setLoadingMechanics] = useState(true);
  const [selectedMechanic, setSelectedMechanic] = useState<Mechanic | null>(null);
  const [carNumber, setCarNumber] = useState('');
  const [mileage, setMileage] = useState('');
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [answers, setAnswers] = useState<DiagnosticAnswer[]>([]);

  useEffect(() => {
    loadMechanics();
  }, []);

  const loadMechanics = async () => {
    setLoadingMechanics(true);
    try {
      const response = await fetch('https://functions.poehali.dev/47f92079-1392-4766-911a-8aa94a4d8db9');
      if (!response.ok) throw new Error('Ошибка загрузки');
      const data = await response.json();
      setMechanics(data);
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось загрузить список механиков', variant: 'destructive' });
    } finally {
      setLoadingMechanics(false);
    }
  };

  const availableSections = useMemo(() => {
    return priemkaSections.filter(section => {
      if (!section.conditional) return true;
      const dependentAnswer = answers.find(a => a.questionId === section.conditional?.dependsOn);
      return dependentAnswer?.value === section.conditional?.value;
    });
  }, [answers]);

  const currentSection = availableSections[currentSectionIndex];

  const handleAnswer = (questionId: string, value: string) => {
    setAnswers(prev => {
      const existing = prev.findIndex(a => a.questionId === questionId);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = { ...updated[existing], questionId, value };
        return updated;
      }
      return [...prev, { questionId, value, photos: [] }];
    });
  };

  const handleTextComment = (questionId: string, textComment: string) => {
    setAnswers(prev => {
      const existing = prev.findIndex(a => a.questionId === questionId);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = { ...updated[existing], textComment };
        return updated;
      }
      return prev;
    });
  };

  const getTextComment = (questionId: string): string => {
    const answer = answers.find(a => a.questionId === questionId);
    return answer?.textComment || '';
  };

  const handleNext = () => {
    if (currentSectionIndex < availableSections.length - 1) {
      setCurrentSectionIndex(prev => prev + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex(prev => prev - 1);
    }
  };

  const handleComplete = () => {
    const data: DiagnosticData = {
      id: crypto.randomUUID(),
      type: 'priemka',
      mechanicId: selectedMechanic?.id || 0,
      mechanicName: selectedMechanic?.name || '',
      carNumber,
      mileage,
      answers,
      createdAt: new Date().toISOString(),
    };
    onComplete(data);
  };

  const getCurrentAnswer = (questionId: string): string | null => {
    const answer = answers.find(a => a.questionId === questionId);
    return answer?.value as string || null;
  };

  const isCurrentSectionComplete = () => {
    if (!currentSection) return false;
    return currentSection.questions.every(q => {
      const answer = getCurrentAnswer(q.id);
      if (!answer) return false;
      
      if (q.allowText && answer === 'Иное (указать текстом)') {
        const textComment = getTextComment(q.id);
        return textComment.trim() !== '';
      }
      
      return true;
    });
  };

  const answeredInSection = currentSection?.questions.filter(q => getCurrentAnswer(q.id)).length || 0;
  const totalInSection = currentSection?.questions.length || 0;

  if (step === 'mechanic') {
    return (
      <Card className="w-full max-w-2xl mx-auto bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-slate-100">Выбор механика</CardTitle>
          <CardDescription className="text-slate-400">Выберите механика для проведения приемки автомобиля</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingMechanics ? (
            <div className="text-center text-slate-400 py-8">Загрузка...</div>
          ) : (
            <RadioGroup value={selectedMechanic?.id.toString()} onValueChange={(value) => {
              const mechanic = mechanics.find(m => m.id.toString() === value);
              setSelectedMechanic(mechanic || null);
            }}>
              <div className="space-y-2">
                {mechanics.map((mechanic) => (
                  <div key={mechanic.id} className="flex items-center space-x-2 bg-slate-900/50 p-3 rounded-lg border border-slate-700">
                    <RadioGroupItem value={mechanic.id.toString()} id={`mechanic-${mechanic.id}`} />
                    <Label htmlFor={`mechanic-${mechanic.id}`} className="text-slate-300 cursor-pointer flex-1">
                      {mechanic.name}
                    </Label>
                  </div>
                ))}
              </div>
            </RadioGroup>
          )}
          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={onCancel}>
              Отмена
            </Button>
            <Button 
              onClick={() => setStep('carInfo')}
              disabled={!selectedMechanic}
            >
              Далее
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (step === 'carInfo') {
    return (
      <Card className="w-full max-w-2xl mx-auto bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-slate-100">Информация об автомобиле</CardTitle>
          <CardDescription className="text-slate-400">Введите данные автомобиля для приемки</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="carNumber" className="text-slate-300">Госномер автомобиля</Label>
            <Input
              id="carNumber"
              value={carNumber}
              onChange={(e) => setCarNumber(e.target.value.toUpperCase())}
              placeholder="А123БВ777"
              className="bg-slate-900 border-slate-600 text-slate-100 mt-1"
            />
          </div>
          <div>
            <Label htmlFor="mileage" className="text-slate-300">Пробег (км)</Label>
            <Input
              id="mileage"
              type="number"
              value={mileage}
              onChange={(e) => setMileage(e.target.value)}
              placeholder="50000"
              className="bg-slate-900 border-slate-600 text-slate-100 mt-1"
            />
          </div>
          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={() => setStep('mechanic')}>
              Назад
            </Button>
            <Button 
              onClick={() => setStep('diagnostic')}
              disabled={!carNumber || !mileage}
            >
              Начать приемку
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-2xl mx-auto bg-slate-800 border-slate-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-slate-100">{currentSection?.title}</CardTitle>
            <CardDescription className="text-slate-400 mt-1">
              {carNumber} • {mileage} км • {selectedMechanic?.name}
            </CardDescription>
          </div>
          <Badge variant="outline" className="text-slate-300">
            Раздел {currentSectionIndex + 1} из {availableSections.length}
          </Badge>
        </div>
        <div className="flex items-center gap-2 mt-4">
          <div className="flex-1 bg-slate-700 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all"
              style={{ width: `${(answeredInSection / totalInSection) * 100}%` }}
            />
          </div>
          <span className="text-sm text-slate-400">{answeredInSection}/{totalInSection}</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {currentSection?.questions.map((question) => {
          const currentAnswer = getCurrentAnswer(question.id);
          const showTextInput = question.allowText && currentAnswer === 'Иное (указать текстом)';
          
          return (
            <div key={question.id} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700 space-y-3">
              <Label className="text-slate-100 block">{question.text}</Label>
              {question.type === 'choice' && question.options && (
                <RadioGroup 
                  value={currentAnswer || ''} 
                  onValueChange={(value) => handleAnswer(question.id, value)}
                >
                  <div className="space-y-2">
                    {question.options.map((option) => (
                      <div key={option} className="flex items-center space-x-2">
                        <RadioGroupItem value={option} id={`${question.id}-${option}`} />
                        <Label 
                          htmlFor={`${question.id}-${option}`}
                          className="text-slate-300 cursor-pointer"
                        >
                          {option}
                        </Label>
                      </div>
                    ))}
                  </div>
                </RadioGroup>
              )}
              
              {showTextInput && (
                <div className="pt-2">
                  <Label className="text-slate-400 text-sm">Укажите подробнее:</Label>
                  <Textarea
                    value={getTextComment(question.id)}
                    onChange={(e) => handleTextComment(question.id, e.target.value)}
                    placeholder="Введите текст..."
                    className="bg-slate-800 border-slate-600 mt-1"
                    rows={3}
                  />
                </div>
              )}
              
              {question.allowPhoto && currentAnswer && (
                <div className="pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex items-center gap-2"
                    onClick={() => toast({ title: 'Функция в разработке', description: 'Загрузка фото будет доступна позже' })}
                  >
                    <Icon name="Camera" size={16} />
                    Прикрепить фото (опционально)
                  </Button>
                </div>
              )}
            </div>
          );
        })}

        <div className="flex justify-between pt-4">
          <Button 
            variant="outline" 
            onClick={handleBack}
            disabled={currentSectionIndex === 0}
          >
            <Icon name="ChevronLeft" size={16} className="mr-1" />
            Назад
          </Button>
          <Button 
            onClick={handleNext}
            disabled={!isCurrentSectionComplete()}
          >
            {currentSectionIndex === availableSections.length - 1 ? 'Завершить' : 'Далее'}
            {currentSectionIndex < availableSections.length - 1 && <Icon name="ChevronRight" size={16} className="ml-1" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default DiagnosticPriemka;
