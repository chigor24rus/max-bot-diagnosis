import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';

interface DiagnosticSelectorProps {
  mechanicName: string;
  onSelectType: (type: 'dhch' | '5min' | 'des') => void;
  onCancel: () => void;
}

const DiagnosticSelector = ({ mechanicName, onSelectType, onCancel }: DiagnosticSelectorProps) => {
  return (
    <Card className="bg-slate-950/90 border-primary/20">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Icon name="ClipboardList" size={24} className="text-primary" />
          Выбор типа диагностики
        </CardTitle>
        <CardDescription>Механик: {mechanicName}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        <Button
          onClick={() => onSelectType('dhch')}
          className="w-full justify-start h-auto py-4"
          variant="outline"
        >
          <div className="flex items-start gap-3 text-left">
            <Icon name="Wrench" size={24} className="text-primary mt-1 flex-shrink-0" />
            <div>
              <div className="font-semibold text-white">ДХЧ</div>
              <div className="text-sm text-slate-400">Диагностика ходовой части</div>
            </div>
          </div>
        </Button>

        <Button
          onClick={() => onSelectType('5min')}
          className="w-full justify-start h-auto py-4"
          variant="outline"
          disabled
        >
          <div className="flex items-start gap-3 text-left">
            <Icon name="Clock" size={24} className="text-slate-500 mt-1 flex-shrink-0" />
            <div>
              <div className="font-semibold text-slate-400">5-ти минутка</div>
              <div className="text-sm text-slate-500">Быстрый осмотр (скоро)</div>
            </div>
          </div>
        </Button>

        <Button
          onClick={() => onSelectType('des')}
          className="w-full justify-start h-auto py-4"
          variant="outline"
          disabled
        >
          <div className="flex items-start gap-3 text-left">
            <Icon name="Zap" size={24} className="text-slate-500 mt-1 flex-shrink-0" />
            <div>
              <div className="font-semibold text-slate-400">ДЭС</div>
              <div className="text-sm text-slate-500">Диагностика электросистем (скоро)</div>
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
