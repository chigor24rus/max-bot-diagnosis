import { useState, useMemo, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';
import { dhchSections } from '@/data/dhch-checklist';
import { DiagnosticData, DiagnosticAnswer, Section } from '@/types/diagnostic';

interface DiagnosticDHCHProps {
  onComplete: (data: DiagnosticData) => void;
  onCancel: () => void;
}

type Mechanic = {
  id: number;
  name: string;
};

const DiagnosticDHCH = ({ onComplete, onCancel }: DiagnosticDHCHProps) => {
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

  const activeSections = useMemo(() => {
    const driveTypeAnswer = answers.find(a => a.questionId === 'drive_type');
    
    if (!driveTypeAnswer) {
      return [dhchSections[0]];
    }

    const sections: Section[] = [dhchSections[0]];
    
    dhchSections.slice(1).forEach(section => {
      if (section.conditional) {
        const dependsOnAnswer = answers.find(a => a.questionId === section.conditional!.dependsOn);
        if (dependsOnAnswer && dependsOnAnswer.value === section.conditional.value) {
          sections.push(section);
        }
      }
    });

    return sections;
  }, [answers]);

  const currentSection = activeSections[currentSectionIndex];
  const progress = currentSection ? ((currentSectionIndex + 1) / activeSections.length) * 100 : 0;
  const isLastSection = currentSectionIndex === activeSections.length - 1;

  const handleMechanicSelect = (mechanic: Mechanic) => {
    setSelectedMechanic(mechanic);
  };

  const handleMechanicNext = () => {
    if (!selectedMechanic) {
      toast({ title: 'Выберите механика', variant: 'destructive' });
      return;
    }
    setStep('carInfo');
  };

  const handleCarInfoNext = () => {
    if (!carNumber.trim()) {
      toast({ title: 'Ошибка', description: 'Введите гос.номер', variant: 'destructive' });
      return;
    }
    if (!mileage || parseInt(mileage) <= 0) {
      toast({ title: 'Ошибка', description: 'Введите корректный пробег', variant: 'destructive' });
      return;
    }
    setStep('diagnostic');
  };

  const handleAnswer = (questionId: string, value: string) => {
    setAnswers(prev => {
      const existing = prev.findIndex(a => a.questionId === questionId);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = { questionId, value };
        return updated;
      }
      return [...prev, { questionId, value, photos: [] }];
    });
  };

  const getCurrentAnswer = (questionId: string): string | null => {
    const answer = answers.find(a => a.questionId === questionId);
    return answer?.value as string || null;
  };

  const isCurrentSectionComplete = () => {
    if (!currentSection) return false;
    return currentSection.questions.every(q => {
      const answer = getCurrentAnswer(q.id);
      return answer !== null && answer !== '';
    });
  };

  const handleNext = () => {
    if (!isCurrentSectionComplete()) {
      toast({ 
        title: 'Заполните все вопросы', 
        description: 'Ответьте на все вопросы раздела',
        variant: 'destructive' 
      });
      return;
    }

    if (isLastSection) {
      const diagnosticData: DiagnosticData = {
        mechanicId: selectedMechanic!.id,
        mechanicName: selectedMechanic!.name,
        carNumber: carNumber.trim(),
        mileage: parseInt(mileage),
        diagnosticType: 'ДХЧ',
        answers,
        currentSection: currentSection.id,
        completedSections: activeSections.map(s => s.id)
      };
      onComplete(diagnosticData);
    } else {
      setCurrentSectionIndex(prev => prev + 1);
    }
  };

  const handleBack = () => {
    if (currentSectionIndex > 0) {
      setCurrentSectionIndex(prev => prev - 1);
    } else if (step === 'diagnostic') {
      setStep('carInfo');
    } else if (step === 'carInfo') {
      setStep('mechanic');
    }
  };

  // Шаг 1: Выбор механика
  if (step === 'mechanic') {
    return (
      <Card className="bg-slate-950/90 border-primary/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Icon name="Wrench" size={24} className="text-primary" />
            Диагностика ДХЧ
          </CardTitle>
          <CardDescription>Выберите механика</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loadingMechanics ? (
            <div className="text-center py-8">
              <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-slate-400">Загрузка механиков...</p>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 gap-2">
                {mechanics.map((mechanic) => (
                  <Button
                    key={mechanic.id}
                    variant={selectedMechanic?.id === mechanic.id ? 'default' : 'outline'}
                    className="w-full justify-start text-left h-auto py-3"
                    onClick={() => handleMechanicSelect(mechanic)}
                  >
                    <Icon name="User" size={20} className="mr-2 flex-shrink-0" />
                    {mechanic.name}
                  </Button>
                ))}
              </div>
              <div className="flex gap-3 pt-4">
                <Button 
                  onClick={handleMechanicNext} 
                  className="flex-1"
                  disabled={!selectedMechanic}
                >
                  Далее
                  <Icon name="ChevronRight" size={16} className="ml-2" />
                </Button>
                <Button variant="outline" onClick={onCancel}>
                  Отмена
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    );
  }

  // Шаг 2: Ввод данных автомобиля
  if (step === 'carInfo') {
    return (
      <Card className="bg-slate-950/90 border-primary/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Icon name="Wrench" size={24} className="text-primary" />
            Диагностика ДХЧ
          </CardTitle>
          <CardDescription>Механик: {selectedMechanic?.name}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-slate-300">Гос. номер автомобиля</Label>
            <Input 
              value={carNumber}
              onChange={(e) => setCarNumber(e.target.value.toUpperCase())}
              placeholder="А123БВ199"
              className="bg-slate-900 border-slate-700"
              autoFocus
            />
          </div>
          <div>
            <Label className="text-slate-300">Пробег (км)</Label>
            <Input 
              type="number"
              value={mileage}
              onChange={(e) => setMileage(e.target.value)}
              placeholder="50000"
              className="bg-slate-900 border-slate-700"
            />
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleBack}>
              <Icon name="ChevronLeft" size={16} className="mr-2" />
              Назад
            </Button>
            <Button onClick={handleCarInfoNext} className="flex-1">
              Начать диагностику
              <Icon name="Play" size={16} className="ml-2" />
            </Button>
            <Button variant="outline" onClick={onCancel}>
              Отмена
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Шаг 3: Прохождение диагностики
  return (
    <Card className="bg-slate-950/90 border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <CardTitle className="text-white flex items-center gap-2">
            <Icon name="Wrench" size={24} className="text-primary" />
            {currentSection?.title}
          </CardTitle>
          <Badge variant="outline">
            {currentSectionIndex + 1} / {activeSections.length}
          </Badge>
        </div>
        <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
          <div 
            className="bg-primary h-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <CardDescription className="mt-2">
          {carNumber} • {parseInt(mileage).toLocaleString()} км • {selectedMechanic?.name}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {currentSection?.questions.map((question) => (
          <div key={question.id} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
            <Label className="text-slate-100 mb-3 block">{question.text}</Label>
            {question.type === 'choice' && question.options && (
              <RadioGroup 
                value={getCurrentAnswer(question.id) || ''} 
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
          </div>
        ))}

        <div className="flex gap-3 pt-4">
          <Button variant="outline" onClick={handleBack}>
            <Icon name="ChevronLeft" size={16} className="mr-2" />
            Назад
          </Button>
          <Button 
            onClick={handleNext} 
            className="flex-1"
            disabled={!isCurrentSectionComplete()}
          >
            {isLastSection ? 'Завершить' : 'Далее'}
            {!isLastSection && <Icon name="ChevronRight" size={16} className="ml-2" />}
          </Button>
          <Button variant="destructive" onClick={onCancel}>
            Отменить
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default DiagnosticDHCH;
