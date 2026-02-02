import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import Icon from '@/components/ui/icon';
import { checklistQuestions, type ChecklistQuestion, type AnswerOption } from '@/data/checklistData';

type Answer = {
  questionId: number;
  questionText: string;
  answerValue: string;
  answerLabel: string;
  subAnswers?: Record<string, any>;
  textInput?: string;
  photoUrls?: string[];
};

type ChecklistWizardProps = {
  onComplete: (answers: Answer[]) => void;
  onCancel: () => void;
};

const ChecklistWizard = ({ onComplete, onCancel }: ChecklistWizardProps) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selectedOption, setSelectedOption] = useState<string>('');
  const [subSelections, setSubSelections] = useState<Record<string, string | string[]>>({});
  const [textInput, setTextInput] = useState('');
  const [photoFiles, setPhotoFiles] = useState<File[]>([]);
  const [showSubOptions, setShowSubOptions] = useState(false);

  const currentQuestion = checklistQuestions[currentQuestionIndex];
  const progress = ((currentQuestionIndex + 1) / checklistQuestions.length) * 100;

  const handleOptionSelect = (option: AnswerOption) => {
    setSelectedOption(option.value);
    setShowSubOptions(!!option.subOptions && option.subOptions.length > 0);
    setSubSelections({});
    setTextInput('');
  };

  const handleSubOptionSelect = (parentKey: string, subOption: AnswerOption) => {
    setSubSelections((prev) => ({
      ...prev,
      [parentKey]: subOption.value,
    }));
  };

  const handlePhotoUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPhotoFiles(Array.from(e.target.files));
    }
  };

  const canProceed = (): boolean => {
    if (!selectedOption) return false;

    const selectedOpt = currentQuestion.options.find((o) => o.value === selectedOption);
    if (!selectedOpt) return false;

    if (selectedOpt.requiresText && !textInput.trim()) return false;

    if (selectedOpt.subOptions && selectedOpt.subOptions.length > 0) {
      return Object.keys(subSelections).length > 0;
    }

    return true;
  };

  const handleNext = async () => {
    if (!canProceed()) return;

    const selectedOpt = currentQuestion.options.find((o) => o.value === selectedOption);
    if (!selectedOpt) return;

    let photoUrls: string[] = [];
    if (photoFiles.length > 0) {
      photoUrls = await uploadPhotos(photoFiles);
    }

    const answer: Answer = {
      questionId: currentQuestion.id,
      questionText: currentQuestion.title,
      answerValue: selectedOption,
      answerLabel: selectedOpt.label,
      subAnswers: Object.keys(subSelections).length > 0 ? subSelections : undefined,
      textInput: textInput.trim() || undefined,
      photoUrls: photoUrls.length > 0 ? photoUrls : undefined,
    };

    const newAnswers = [...answers, answer];
    setAnswers(newAnswers);

    if (selectedOpt.skipToQuestion) {
      const targetIndex = checklistQuestions.findIndex((q) => q.id === selectedOpt.skipToQuestion);
      if (targetIndex !== -1) {
        setCurrentQuestionIndex(targetIndex);
      } else {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
      }
    } else if (currentQuestionIndex < checklistQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      onComplete(newAnswers);
      return;
    }

    setSelectedOption('');
    setSubSelections({});
    setTextInput('');
    setPhotoFiles([]);
    setShowSubOptions(false);
  };

  const handleBack = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
      const prevAnswer = answers[answers.length - 1];
      if (prevAnswer) {
        setSelectedOption(prevAnswer.answerValue);
        setSubSelections(prevAnswer.subAnswers || {});
        setTextInput(prevAnswer.textInput || '');
        setShowSubOptions(!!prevAnswer.subAnswers);
      }
      setAnswers(answers.slice(0, -1));
      setPhotoFiles([]);
    } else {
      onCancel();
    }
  };

  const uploadPhotos = async (files: File[]): Promise<string[]> => {
    const uploadedUrls: string[] = [];
    
    for (const file of files) {
      try {
        const reader = new FileReader();
        const base64 = await new Promise<string>((resolve, reject) => {
          reader.onload = () => {
            const result = reader.result as string;
            const base64Data = result.split(',')[1];
            resolve(base64Data);
          };
          reader.onerror = reject;
          reader.readAsDataURL(file);
        });
        
        const response = await fetch('https://functions.poehali.dev/b394c821-025d-42c4-aa3a-200c10a6ddc0', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            image: base64,
            filename: file.name,
          }),
        });
        
        if (response.ok) {
          const data = await response.json();
          uploadedUrls.push(data.url);
        }
      } catch (error) {
        console.error('Failed to upload photo:', error);
      }
    }
    
    return uploadedUrls;
  };

  const renderSubOptions = (parentOption: AnswerOption, parentKey: string = 'main') => {
    if (!parentOption.subOptions || parentOption.subOptions.length === 0) return null;

    const isMultiple = parentOption.allowMultiple;
    const currentSelection = subSelections[parentKey];
    const selectedValues = isMultiple && Array.isArray(currentSelection) ? currentSelection : [];

    const handleMultiSelect = (subOpt: AnswerOption) => {
      if (isMultiple) {
        const newSelection = selectedValues.includes(subOpt.value)
          ? selectedValues.filter(v => v !== subOpt.value)
          : [...selectedValues, subOpt.value];
        setSubSelections({ ...subSelections, [parentKey]: newSelection });
      } else {
        handleSubOptionSelect(parentKey, subOpt);
      }
    };

    return (
      <div className="ml-6 mt-3 space-y-2">
        <div className="text-sm text-slate-300 font-medium">
          {isMultiple ? 'Выберите все что подходит:' : 'Выберите детали:'}
        </div>
        {parentOption.subOptions.map((subOpt) => {
          const isSelected = isMultiple 
            ? selectedValues.includes(subOpt.value)
            : subSelections[parentKey] === subOpt.value;

          return (
            <div key={`${parentKey}-${subOpt.value}`}>
              <Button
                variant={isSelected ? 'default' : 'outline'}
                className="w-full justify-start text-left"
                onClick={() => handleMultiSelect(subOpt)}
              >
                {isMultiple && (
                  <Icon 
                    name={isSelected ? 'CheckSquare' : 'Square'} 
                    size={16} 
                    className="mr-2" 
                  />
                )}
                {subOpt.label}
              </Button>
              {!isMultiple && isSelected && subOpt.subOptions && (
                <div className="ml-4 mt-2">
                  {renderSubOptions(subOpt, `${parentKey}-${subOpt.value}`)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <Card className="w-full max-w-3xl mx-auto bg-slate-950/90 border-primary/20">
      <CardHeader>
        <div className="flex items-center justify-between mb-2">
          <CardTitle className="text-white text-lg">
            Вопрос {currentQuestion.id} из {checklistQuestions.length}
          </CardTitle>
          <span className="text-sm text-slate-400">{progress.toFixed(0)}%</span>
        </div>
        <Progress value={progress} className="h-2" />
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
          <h3 className="text-xl font-semibold text-white mb-4">{currentQuestion.title}</h3>

          <div className="space-y-2">
            {currentQuestion.options.map((option) => (
              <div key={option.value}>
                <Button
                  variant={selectedOption === option.value ? 'default' : 'outline'}
                  className="w-full justify-start text-left"
                  onClick={() => handleOptionSelect(option)}
                >
                  <Icon
                    name={selectedOption === option.value ? 'CheckCircle' : 'Circle'}
                    size={18}
                    className="mr-2 flex-shrink-0"
                  />
                  {option.label}
                </Button>

                {selectedOption === option.value && showSubOptions && (
                  <div className="mt-2">{renderSubOptions(option)}</div>
                )}

                {selectedOption === option.value && option.requiresText && (
                  <div className="mt-3">
                    <Textarea
                      placeholder="Введите дополнительную информацию..."
                      value={textInput}
                      onChange={(e) => setTextInput(e.target.value)}
                      className="bg-slate-900/50 border-slate-700 text-white"
                      rows={3}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>

          {(currentQuestion.requiresPhoto || 
            (selectedOption && currentQuestion.options.find(o => o.value === selectedOption)?.allowMultiple)) && (
            <div className="mt-4">
              <label className="block text-sm text-slate-300 mb-2">
                <Icon name="Camera" size={16} className="inline mr-1" />
                Прикрепить фото (опционально)
              </label>
              <Input
                type="file"
                accept="image/*"
                multiple
                onChange={handlePhotoUpload}
                className="bg-slate-900/50 border-slate-700 text-white"
              />
              {photoFiles.length > 0 && (
                <div className="mt-2 text-sm text-slate-400">
                  Выбрано файлов: {photoFiles.length}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center justify-between gap-3">
          <Button variant="outline" onClick={handleBack} className="flex items-center gap-2">
            <Icon name="ChevronLeft" size={16} />
            Назад
          </Button>

          <Button
            onClick={handleNext}
            disabled={!canProceed()}
            className="flex items-center gap-2"
          >
            {currentQuestionIndex === checklistQuestions.length - 1 ? (
              <>
                <Icon name="Check" size={16} />
                Завершить
              </>
            ) : (
              <>
                Далее
                <Icon name="ChevronRight" size={16} />
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ChecklistWizard;