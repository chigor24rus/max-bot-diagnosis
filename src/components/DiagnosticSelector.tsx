import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';

interface DiagnosticSelectorProps {
  onSelectType: (type: 'priemka' | 'dhch' | '5min' | 'des') => void;
  onCancel: () => void;
}

const DiagnosticSelector = ({ onSelectType, onCancel }: DiagnosticSelectorProps) => {
  return (
    <Card className="bg-slate-950/90 border-primary/20">
      <CardHeader className="p-4 sm:p-6">
        <CardTitle className="text-white flex items-center gap-2 text-lg sm:text-xl">
          <Icon name="ClipboardList" size={20} className="text-primary sm:w-6 sm:h-6" />
          Выбор типа диагностики
        </CardTitle>
        <CardDescription className="text-sm">Выберите тип диагностики для проведения</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3 p-4 sm:p-6">
        <Button
          onClick={() => onSelectType('priemka')}
          className="w-full justify-start h-auto py-3 sm:py-4"
          variant="outline"
        >
          <div className="flex items-start gap-2 sm:gap-3 text-left">
            <Icon name="ClipboardCheck" size={20} className="text-primary mt-0.5 sm:mt-1 flex-shrink-0 sm:w-6 sm:h-6" />
            <div>
              <div className="font-semibold text-white text-sm sm:text-base">Приемка</div>
              <div className="text-xs sm:text-sm text-slate-400">Приемка автомобиля</div>
            </div>
          </div>
        </Button>

        <Button
          onClick={() => onSelectType('5min')}
          className="w-full justify-start h-auto py-3 sm:py-4"
          variant="outline"
          disabled
        >
          <div className="flex items-start gap-2 sm:gap-3 text-left">
            <Icon name="Clock" size={20} className="text-slate-500 mt-0.5 sm:mt-1 flex-shrink-0 sm:w-6 sm:h-6" />
            <div>
              <div className="font-semibold text-slate-400 text-sm sm:text-base">5-ти минутка</div>
              <div className="text-xs sm:text-sm text-slate-500">Быстрый осмотр (скоро)</div>
            </div>
          </div>
        </Button>

        <Button
          onClick={() => onSelectType('dhch')}
          className="w-full justify-start h-auto py-3 sm:py-4"
          variant="outline"
          disabled
        >
          <div className="flex items-start gap-2 sm:gap-3 text-left">
            <Icon name="Wrench" size={20} className="text-slate-500 mt-0.5 sm:mt-1 flex-shrink-0 sm:w-6 sm:h-6" />
            <div>
              <div className="font-semibold text-slate-400 text-sm sm:text-base">ДХЧ</div>
              <div className="text-xs sm:text-sm text-slate-500">Раздел в разработке</div>
            </div>
          </div>
        </Button>

        <Button
          onClick={() => onSelectType('des')}
          className="w-full justify-start h-auto py-3 sm:py-4"
          variant="outline"
          disabled
        >
          <div className="flex items-start gap-2 sm:gap-3 text-left">
            <Icon name="Zap" size={20} className="text-slate-500 mt-0.5 sm:mt-1 flex-shrink-0 sm:w-6 sm:h-6" />
            <div>
              <div className="font-semibold text-slate-400 text-sm sm:text-base">ДЭС</div>
              <div className="text-xs sm:text-sm text-slate-500">Раздел в разработке</div>
            </div>
          </div>
        </Button>

        <Button
          onClick={onCancel}
          variant="ghost"
          className="w-full mt-4"
        >
          Отмена
        </Button>
      </CardContent>
    </Card>
  );
};

export default DiagnosticSelector;