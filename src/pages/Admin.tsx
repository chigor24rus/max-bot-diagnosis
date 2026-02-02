import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import Icon from '@/components/ui/icon';
import { Badge } from '@/components/ui/badge';

const Admin = () => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);

  const webhookUrl = 'https://functions.poehali.dev/f48b0eea-37b1-4cf5-a470-aa20ae0fd775';
  const setupUrl = 'https://functions.poehali.dev/8e7d060d-23fb-4628-88e9-e251279d6a28';

  const loadSubscriptions = async () => {
    setLoading(true);
    try {
      const response = await fetch(setupUrl);
      if (!response.ok) throw new Error('Ошибка загрузки');
      
      const data = await response.json();
      setSubscriptions(data.subscriptions?.subscriptions || []);
      
      toast({
        title: 'Готово',
        description: `Загружено подписок: ${data.subscriptions?.subscriptions?.length || 0}`
      });
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить подписки',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const createSubscription = async () => {
    setLoading(true);
    try {
      const response = await fetch(setupUrl, { method: 'POST' });
      if (!response.ok) throw new Error('Ошибка создания');
      
      const data = await response.json();
      
      toast({
        title: '✅ Webhook настроен!',
        description: 'Бот готов принимать сообщения'
      });
      
      await loadSubscriptions();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось настроить webhook',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const deleteSubscriptions = async () => {
    setLoading(true);
    try {
      const response = await fetch(setupUrl, { method: 'DELETE' });
      if (!response.ok) throw new Error('Ошибка удаления');
      
      const data = await response.json();
      
      toast({
        title: 'Готово',
        description: data.message
      });
      
      setSubscriptions([]);
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось удалить подписки',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card className="bg-slate-950/90 border-primary/20">
          <CardHeader>
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                <Icon name="Settings" size={24} className="text-white" />
              </div>
              <div>
                <CardTitle className="text-white">Админ-панель</CardTitle>
                <CardDescription>Управление интеграцией с MAX ботом</CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>

        <Card className="bg-slate-950/90 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Icon name="Webhook" size={20} className="text-primary" />
              Настройка Webhook
            </CardTitle>
            <CardDescription>
              Подключите бота к webhook для приёма сообщений
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
              <div className="text-sm text-slate-400 mb-2">Webhook URL:</div>
              <div className="flex items-center gap-2">
                <code className="flex-1 bg-slate-800 px-3 py-2 rounded text-primary text-sm overflow-x-auto">
                  {webhookUrl}
                </code>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    navigator.clipboard.writeText(webhookUrl);
                    toast({ title: 'Скопировано!', description: 'URL скопирован в буфер обмена' });
                  }}
                >
                  <Icon name="Copy" size={16} />
                </Button>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <Button
                onClick={createSubscription}
                disabled={loading}
                className="flex items-center gap-2"
              >
                <Icon name="Plus" size={16} />
                Создать подписку
              </Button>
              
              <Button
                onClick={loadSubscriptions}
                disabled={loading}
                variant="outline"
                className="flex items-center gap-2"
              >
                <Icon name="RefreshCw" size={16} />
                Проверить статус
              </Button>
              
              <Button
                onClick={deleteSubscriptions}
                disabled={loading}
                variant="destructive"
                className="flex items-center gap-2"
              >
                <Icon name="Trash2" size={16} />
                Удалить подписки
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-950/90 border-slate-700">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Icon name="List" size={20} className="text-primary" />
              Активные подписки
            </CardTitle>
          </CardHeader>
          <CardContent>
            {subscriptions.length === 0 ? (
              <div className="text-center py-8 text-slate-400">
                <Icon name="InboxIcon" size={48} className="mx-auto mb-3 opacity-50" />
                <p>Нет активных подписок</p>
                <p className="text-sm mt-1">Создайте подписку для активации бота</p>
              </div>
            ) : (
              <div className="space-y-3">
                {subscriptions.map((sub, idx) => (
                  <div key={idx} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="bg-green-500/10 text-green-400 border-green-500/30">
                            Активна
                          </Badge>
                          <span className="text-xs text-slate-500">
                            {new Date(sub.time).toLocaleString('ru-RU')}
                          </span>
                        </div>
                        <div className="text-sm text-slate-300 break-all">
                          {sub.url}
                        </div>
                        {sub.update_types && (
                          <div className="flex flex-wrap gap-2">
                            {sub.update_types.map((type: string) => (
                              <Badge key={type} variant="outline" className="text-xs">
                                {type}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

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
      </div>
    </div>
  );
};

export default Admin;
