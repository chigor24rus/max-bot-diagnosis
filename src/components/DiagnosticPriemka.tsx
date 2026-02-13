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
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
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
  const currentQuestion = currentSection?.questions[currentQuestionIndex];

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
    const totalQuestions = currentSection?.questions.length || 0;
    
    if (currentQuestionIndex < totalQuestions - 1) {
      setCurrentQuestionIndex(prev => prev + 1);
    } else if (currentSectionIndex < availableSections.length - 1) {
      setCurrentSectionIndex(prev => prev + 1);
      setCurrentQuestionIndex(0);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(prev => prev - 1);
    } else if (currentSectionIndex > 0) {
      setCurrentSectionIndex(prev => prev - 1);
      const prevSection = availableSections[currentSectionIndex - 1];
      setCurrentQuestionIndex((prevSection?.questions.length || 1) - 1);
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

  const isCurrentQuestionComplete = () => {
    if (!currentQuestion) return false;
    const answer = getCurrentAnswer(currentQuestion.id);
    
    if (currentQuestion.type === 'photo') {
      return answer !== null && answer !== '';
    }
    
    if (!answer) return false;
    
    if (currentQuestion.allowText && answer === 'Добавить замечания (указать текстом)') {
      const textComment = getTextComment(currentQuestion.id);
      return textComment.trim() !== '';
    }
    
    return true;
  };

  const totalQuestions = availableSections.reduce((sum, section) => sum + section.questions.length, 0);
  const answeredQuestions = availableSections.reduce((sum, section) => 
    sum + section.questions.filter(q => getCurrentAnswer(q.id)).length, 0
  );
  const currentGlobalQuestionNumber = availableSections
    .slice(0, currentSectionIndex)
    .reduce((sum, section) => sum + section.questions.length, 0) + currentQuestionIndex + 1;

  if (step === 'mechanic') {
    return (
      <Card className="w-full max-w-2xl mx-auto bg-slate-800 border-slate-700">
        <CardHeader className="p-4 sm:p-6">
          <CardTitle className="text-slate-100 text-lg sm:text-xl">Выбор механика</CardTitle>
          <CardDescription className="text-slate-400 text-sm">Выберите механика для проведения приемки автомобиля</CardDescription>
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
          <div className="flex flex-col-reverse sm:flex-row justify-between gap-2 sm:gap-0 pt-4">
            <Button variant="outline" onClick={onCancel} className="w-full sm:w-auto">
              Отмена
            </Button>
            <Button 
              onClick={() => setStep('carInfo')}
              disabled={!selectedMechanic}
              className="w-full sm:w-auto"
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
        <CardHeader className="p-4 sm:p-6">
          <CardTitle className="text-slate-100 text-lg sm:text-xl">Информация об автомобиле</CardTitle>
          <CardDescription className="text-slate-400 text-sm">Введите данные автомобиля для приемки</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4 p-4 sm:p-6">
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
          <div className="flex flex-col-reverse sm:flex-row justify-between gap-2 sm:gap-0 pt-4">
            <Button variant="outline" onClick={() => setStep('mechanic')} className="w-full sm:w-auto">
              Назад
            </Button>
            <Button 
              onClick={() => setStep('diagnostic')}
              disabled={!carNumber || !mileage}
              className="w-full sm:w-auto"
            >
              Начать приемку
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!currentQuestion) return null;

  const currentAnswer = getCurrentAnswer(currentQuestion.id);
  const showTextInput = currentQuestion.allowText && currentAnswer === 'Добавить замечания (указать текстом)';
  const isLastQuestion = currentSectionIndex === availableSections.length - 1 && 
                         currentQuestionIndex === (currentSection?.questions.length || 0) - 1;

  return (
    <Card className="w-full max-w-2xl mx-auto bg-slate-800 border-slate-700">
      <CardHeader className="p-4 sm:p-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 sm:gap-0">
          <div className="min-w-0 flex-1">
            <CardTitle className="text-slate-100 text-base sm:text-xl truncate">{currentSection?.title}</CardTitle>
            <CardDescription className="text-slate-400 mt-1 text-xs sm:text-sm truncate">
              {carNumber} • {mileage} км • {selectedMechanic?.name}
            </CardDescription>
          </div>
          <Badge variant="outline" className="text-slate-300 text-xs sm:text-sm shrink-0">
            {currentGlobalQuestionNumber}/{totalQuestions}
          </Badge>
        </div>
        <div className="flex items-center gap-2 mt-4">
          <div className="flex-1 bg-slate-700 rounded-full h-2">
            <div 
              className="bg-blue-500 h-2 rounded-full transition-all"
              style={{ width: `${(answeredQuestions / totalQuestions) * 100}%` }}
            />
          </div>
          <span className="text-sm text-slate-400">{answeredQuestions}/{totalQuestions}</span>
        </div>
      </CardHeader>
      <CardContent className="space-y-4 sm:space-y-6 p-4 sm:p-6">
        <div className="bg-slate-900/50 rounded-lg p-4 sm:p-6 border border-slate-700 space-y-3 sm:space-y-4 min-h-[250px] sm:min-h-[300px]">
          <Label className="text-slate-100 block font-medium text-base sm:text-lg leading-snug">{currentQuestion.text}</Label>
          
          {currentQuestion.type === 'photo' && (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm text-slate-400">
                <Icon name="ImagePlus" size={18} className="text-orange-400" />
                <span>Прикрепление фото обязательно</span>
              </div>
              <Button
                variant={currentAnswer ? "default" : "outline"}
                size="lg"
                className="w-full flex items-center justify-center gap-2 sm:gap-3 h-12 sm:h-14 text-sm sm:text-base"
                onClick={() => {
                  toast({ title: 'Функция в разработке', description: 'Загрузка фото будет доступна позже' });
                  handleAnswer(currentQuestion.id, 'Фото прикреплено');
                }}
              >
                <Icon name="Camera" size={20} className="sm:w-6 sm:h-6" />
                {currentAnswer ? 'Фото прикреплено ✓' : 'Прикрепить фото'}
              </Button>
            </div>
          )}
          
          {currentQuestion.type === 'choice' && currentQuestion.options && (
            <RadioGroup 
              value={currentAnswer || ''} 
              onValueChange={(value) => handleAnswer(currentQuestion.id, value)}
            >
              <div className="space-y-3">
                {currentQuestion.options.map((option) => (
                  <div key={option} className="flex items-center space-x-3 bg-slate-800/50 p-3 rounded-lg hover:bg-slate-800 transition-colors">
                    <RadioGroupItem value={option} id={`${currentQuestion.id}-${option}`} />
                    <Label 
                      htmlFor={`${currentQuestion.id}-${option}`}
                      className="text-slate-300 cursor-pointer flex-1"
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
                value={getTextComment(currentQuestion.id)}
                onChange={(e) => handleTextComment(currentQuestion.id, e.target.value)}
                placeholder="Введите текст..."
                className="bg-slate-800 border-slate-600 mt-2"
                rows={4}
              />
            </div>
          )}
          
          {currentQuestion.allowPhoto && currentQuestion.type === 'choice' && currentAnswer && currentAnswer !== 'Доп. Фото нет' && (
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

        <div className="flex flex-col-reverse sm:flex-row justify-between gap-2 sm:gap-0 pt-4">
          <Button 
            variant="outline" 
            onClick={handleBack}
            disabled={currentSectionIndex === 0 && currentQuestionIndex === 0}
            className="w-full sm:w-auto"
          >
            <Icon name="ChevronLeft" size={16} className="mr-1" />
            Назад
          </Button>
          <Button 
            onClick={handleNext}
            disabled={!isCurrentQuestionComplete()}
            className="w-full sm:w-auto"
          >
            {isLastQuestion ? 'Завершить' : 'Далее'}
            {!isLastQuestion && <Icon name="ChevronRight" size={16} className="ml-1" />}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default DiagnosticPriemka;