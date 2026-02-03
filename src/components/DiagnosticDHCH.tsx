import { useState, useMemo } from 'react';
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
  mechanicName: string;
  onComplete: (data: DiagnosticData) => void;
  onCancel: () => void;
}

const DiagnosticDHCH = ({ mechanicName, onComplete, onCancel }: DiagnosticDHCHProps) => {
  const { toast } = useToast();
  const [step, setStep] = useState<'init' | 'diagnostic'>('init');
  const [carNumber, setCarNumber] = useState('');
  const [mileage, setMileage] = useState('');
  const [currentSectionIndex, setCurrentSectionIndex] = useState(0);
  const [answers, setAnswers] = useState<DiagnosticAnswer[]>([]);

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
  const progress = ((currentSectionIndex + 1) / activeSections.length) * 100;
  const isLastSection = currentSectionIndex === activeSections.length - 1;

  const handleStart = () => {
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
        mechanicName,
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
    }
  };

  if (step === 'init') {
    return (
      <Card className="bg-slate-950/90 border-primary/20">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Icon name="Wrench" size={24} className="text-primary" />
            Диагностика ДХЧ
          </CardTitle>
          <CardDescription>Диагностика ходовой части</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-slate-300">Механик</Label>
            <Input 
              value={mechanicName} 
              disabled 
              className="bg-slate-900 border-slate-700"
            />
          </div>
          <div>
            <Label className="text-slate-300">Гос. номер автомобиля</Label>
            <Input 
              value={carNumber}
              onChange={(e) => setCarNumber(e.target.value.toUpperCase())}
              placeholder="А123БВ199"
              className="bg-slate-900 border-slate-700"
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
            <Button onClick={handleStart} className="flex-1">
              <Icon name="Play" size={16} className="mr-2" />
              Начать диагностику
            </Button>
            <Button variant="outline" onClick={onCancel}>
              Отмена
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-950/90 border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <CardTitle className="text-white flex items-center gap-2">
            <Icon name="Wrench" size={24} className="text-primary" />
            {currentSection.title}
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
          {carNumber} • {parseInt(mileage).toLocaleString()} км
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {currentSection.questions.map((question) => (
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
          {currentSectionIndex > 0 && (
            <Button variant="outline" onClick={handleBack}>
              <Icon name="ChevronLeft" size={16} className="mr-2" />
              Назад
            </Button>
          )}
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
