import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

interface WebhookManagerProps {
  webhookUrl: string;
  setupUrl: string;
}

const WebhookManager = ({ webhookUrl, setupUrl }: WebhookManagerProps) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);

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
            disabled={loading || subscriptions.length === 0}
            variant="destructive"
            className="flex items-center gap-2"
          >
            <Icon name="Trash2" size={16} />
            Удалить подписки
          </Button>
        </div>

        {subscriptions.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm text-slate-400">Активные подписки:</div>
            <div className="space-y-2">
              {subscriptions.map((sub: any, index: number) => (
                <div key={index} className="bg-slate-900/50 rounded-lg p-3 border border-slate-700">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 space-y-1">
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/30">
                          Активна
                        </Badge>
                        <span className="text-xs text-slate-500">ID: {sub.id}</span>
                      </div>
                      <div className="text-xs text-slate-400">
                        <div>URL: {sub.url}</div>
                        {sub.events && (
                          <div className="mt-1">
                            События: {sub.events.map((e: any) => e.type).join(', ')}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default WebhookManager;
