import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

const BotInfo = () => {
  return (
    <div className="p-4 space-y-4">
      <Card className="bg-gradient-to-br from-primary/10 via-slate-900/50 to-accent/10 border-primary/20">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto mb-4 w-24 h-24 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center shadow-2xl">
            <Icon name="Bot" size={48} className="text-white" />
          </div>
          <CardTitle className="text-3xl font-bold text-white">HEVSR Diagnostics bot</CardTitle>
          <div className="flex items-center justify-center gap-2 text-sm text-slate-400 mt-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>Активен • Версия 1.0</span>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="text-center space-y-4">
            <p className="text-slate-100 leading-relaxed">
              Умный помощник для проведения диагностики автомобилей в автосервисе.
              Автоматизирует процесс осмотра, сохраняет данные и генерирует отчёты.
            </p>
            <a 
              href="https://max.ru/id245900919213_bot" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-primary hover:bg-primary/90 text-white px-6 py-3 rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl"
            >
              <Icon name="MessageSquare" size={20} />
              Открыть в MAX мессенджере
            </a>
          </div>

          <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
              <Icon name="Sparkles" size={20} className="text-primary" />
              Возможности
            </h3>
            <ul className="space-y-2 text-slate-100 text-sm">
              <li className="flex items-start gap-2">
                <Icon name="CheckCircle2" size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                <span>Пошаговая диагностика с выбором механика и типа осмотра</span>
              </li>
              <li className="flex items-start gap-2">
                <Icon name="CheckCircle2" size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                <span>Автоматическое сохранение всех данных в базу</span>
              </li>
              <li className="flex items-start gap-2">
                <Icon name="CheckCircle2" size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                <span>Генерация PDF отчётов для печати клиенту</span>
              </li>
              <li className="flex items-start gap-2">
                <Icon name="CheckCircle2" size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                <span>История всех диагностик с поиском и фильтрами</span>
              </li>
              <li className="flex items-start gap-2">
                <Icon name="CheckCircle2" size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                <span>Работает в MAX мессенджере и веб-версии</span>
              </li>
              <li className="flex items-start gap-2">
                <Icon name="CheckCircle2" size={16} className="text-green-400 mt-0.5 flex-shrink-0" />
                <span>Синхронизация данных между всеми устройствами</span>
              </li>
            </ul>
          </div>

          <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
              <Icon name="Terminal" size={20} className="text-primary" />
              Команды
            </h3>
            <div className="space-y-2">
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 font-mono">
                  /start
                </Badge>
                <span className="text-slate-100 text-sm">Начать новую диагностику</span>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 font-mono">
                  /cancel
                </Badge>
                <span className="text-slate-100 text-sm">Отменить текущую операцию</span>
              </div>
              <div className="flex items-center gap-3">
                <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30 font-mono">
                  /help
                </Badge>
                <span className="text-slate-100 text-sm">Показать список команд</span>
              </div>
            </div>
          </div>

          <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
            <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
              <Icon name="Wrench" size={20} className="text-primary" />
              Типы диагностики
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                <div className="text-primary font-semibold mb-1">5-ти минутка</div>
                <div className="text-xs text-slate-200">Быстрый осмотр</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                <div className="text-primary font-semibold mb-1">ДХЧ</div>
                <div className="text-xs text-slate-200">Диагностика ходовой части</div>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
                <div className="text-primary font-semibold mb-1">ДЭС</div>
                <div className="text-xs text-slate-200">Диагностика электросистем</div>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-primary/10 to-accent/10 rounded-lg p-4 border border-primary/20">
            <div className="flex items-start gap-3">
              <Icon name="Info" size={20} className="text-primary mt-0.5 flex-shrink-0" />
              <div className="text-sm text-slate-100">
                <p className="font-semibold mb-1">Совет:</p>
                <p>Бот понимает естественный язык — просто напишите что вам нужно, и он поможет!</p>
              </div>
            </div>
          </div>

          <div className="text-center text-xs text-slate-500 pt-4 border-t border-slate-800">
            <p>Разработано для автосервиса • 2026</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default BotInfo;