import { Card, CardContent } from '@/components/ui/card';
import Icon from '@/components/ui/icon';

const AdminInstructions = () => {
  return (
    <Card className="bg-gradient-to-br from-primary/10 to-accent/10 border-primary/20">
      <CardContent className="pt-6">
        <div className="flex items-start gap-3">
          <Icon name="Info" size={20} className="text-primary mt-0.5 flex-shrink-0" />
          <div className="text-sm text-slate-300">
            <p className="font-semibold mb-2">Инструкция по подключению:</p>
            <ol className="list-decimal list-inside space-y-1 text-slate-400">
              <li>Нажмите "Создать подписку" для активации webhook</li>
              <li>Откройте бота в MAX: https://max.ru/id245900919213_bot</li>
              <li>Отправьте команду /start боту в MAX</li>
              <li>Бот начнёт отвечать на сообщения автоматически</li>
            </ol>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AdminInstructions;
