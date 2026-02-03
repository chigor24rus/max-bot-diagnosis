import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import Icon from '@/components/ui/icon';
import { Badge } from '@/components/ui/badge';
import MechanicsManager from '@/components/MechanicsManager';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const Admin = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [mechanics, setMechanics] = useState<any[]>([]);
  const [diagnostics, setDiagnostics] = useState<any[]>([]);
  const [filteredDiagnostics, setFilteredDiagnostics] = useState<any[]>([]);
  const [newMechanicName, setNewMechanicName] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMechanic, setFilterMechanic] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [deleteMode, setDeleteMode] = useState(false);
  const [deleteDateFrom, setDeleteDateFrom] = useState('');
  const [deleteDateTo, setDeleteDateTo] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      navigate('/login');
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    toast({ title: 'Выход выполнен' });
    navigate('/login');
  };

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

  const loadMechanics = async () => {
    try {
      const response = await fetch('https://functions.poehali.dev/47f92079-1392-4766-911a-8aa94a4d8db9');
      if (!response.ok) throw new Error('Ошибка загрузки');
      const data = await response.json();
      setMechanics(data);
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось загрузить механиков', variant: 'destructive' });
    }
  };

  const loadDiagnostics = async () => {
    try {
      const response = await fetch('https://functions.poehali.dev/e76024e1-4735-4e57-bf5f-060276b574c8');
      if (!response.ok) throw new Error('Ошибка загрузки');
      const data = await response.json();
      setDiagnostics(data);
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось загрузить диагностики', variant: 'destructive' });
    }
  };

  const addMechanic = async () => {
    if (!newMechanicName.trim()) {
      toast({ title: 'Ошибка', description: 'Введите имя механика', variant: 'destructive' });
      return;
    }
    
    try {
      const response = await fetch('https://functions.poehali.dev/47f92079-1392-4766-911a-8aa94a4d8db9', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newMechanicName })
      });
      
      if (!response.ok) throw new Error('Ошибка добавления');
      
      toast({ title: 'Готово', description: 'Механик добавлен' });
      setNewMechanicName('');
      await loadMechanics();
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось добавить механика', variant: 'destructive' });
    }
  };

  const deleteMechanic = async (id: number) => {
    try {
      const response = await fetch(`https://functions.poehali.dev/47f92079-1392-4766-911a-8aa94a4d8db9?id=${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Ошибка удаления');
      
      toast({ title: 'Готово', description: 'Механик удалён' });
      await loadMechanics();
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось удалить механика', variant: 'destructive' });
    }
  };

  const deleteDiagnostic = async (id: number) => {
    try {
      const response = await fetch(`https://functions.poehali.dev/e76024e1-4735-4e57-bf5f-060276b574c8?id=${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Ошибка удаления');
      
      toast({ title: 'Готово', description: 'Диагностика удалена' });
      await loadDiagnostics();
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось удалить диагностику', variant: 'destructive' });
    }
  };

  useEffect(() => {
    loadMechanics();
    loadDiagnostics();
  }, []);

  useEffect(() => {
    let filtered = [...diagnostics];

    if (searchQuery) {
      filtered = filtered.filter(d => 
        d.carNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.mechanic.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (filterMechanic !== 'all') {
      filtered = filtered.filter(d => d.mechanic === filterMechanic);
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(d => d.diagnosticType === filterType);
    }

    if (dateFrom) {
      filtered = filtered.filter(d => new Date(d.createdAt) >= new Date(dateFrom));
    }

    if (dateTo) {
      const endDate = new Date(dateTo);
      endDate.setHours(23, 59, 59, 999);
      filtered = filtered.filter(d => new Date(d.createdAt) <= endDate);
    }

    setFilteredDiagnostics(filtered);
  }, [diagnostics, searchQuery, filterMechanic, filterType, dateFrom, dateTo]);

  const deleteDiagnosticsByDateRange = async () => {
    if (!deleteDateFrom || !deleteDateTo) {
      toast({ 
        title: 'Ошибка', 
        description: 'Укажите период для удаления', 
        variant: 'destructive' 
      });
      return;
    }

    const startDate = new Date(deleteDateFrom);
    const endDate = new Date(deleteDateTo);
    endDate.setHours(23, 59, 59, 999);

    const toDelete = diagnostics.filter(d => {
      const date = new Date(d.createdAt);
      return date >= startDate && date <= endDate;
    });

    if (toDelete.length === 0) {
      toast({ 
        title: 'Нет данных', 
        description: 'В указанном периоде нет диагностик' 
      });
      return;
    }

    if (!confirm(`Удалить ${toDelete.length} диагностик за выбранный период?`)) {
      return;
    }

    setLoading(true);
    let deleted = 0;
    let failed = 0;

    for (const diagnostic of toDelete) {
      try {
        const response = await fetch(
          `https://functions.poehali.dev/e76024e1-4735-4e57-bf5f-060276b574c8?id=${diagnostic.id}`,
          { method: 'DELETE' }
        );
        if (response.ok) {
          deleted++;
        } else {
          failed++;
        }
      } catch (error) {
        failed++;
      }
    }

    setLoading(false);
    toast({ 
      title: 'Готово', 
      description: `Удалено: ${deleted}, ошибок: ${failed}` 
    });
    
    setDeleteMode(false);
    setDeleteDateFrom('');
    setDeleteDateTo('');
    await loadDiagnostics();
  };

  const resetFilters = () => {
    setSearchQuery('');
    setFilterMechanic('all');
    setFilterType('all');
    setDateFrom('');
    setDateTo('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card className="bg-slate-950/90 border-primary/20">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-gradient-to-br from-primary to-accent rounded-lg flex items-center justify-center">
                  <Icon name="Settings" size={24} className="text-white" />
                </div>
                <div>
                  <CardTitle className="text-white">Админ-панель</CardTitle>
                  <CardDescription>Управление интеграцией с MAX ботом</CardDescription>
                </div>
              </div>
              <Button
                variant="outline"
                onClick={handleLogout}
                className="flex items-center gap-2"
              >
                <Icon name="LogOut" size={16} />
                Выйти
              </Button>
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

        <MechanicsManager />

        <Card className="bg-slate-950/90 border-slate-700">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white flex items-center gap-2">
                  <Icon name="ClipboardList" size={20} className="text-primary" />
                  Диагностики
                  <Badge variant="outline" className="ml-2">{filteredDiagnostics.length}</Badge>
                </CardTitle>
                <CardDescription>История сохранённых диагностик</CardDescription>
              </div>
              <Button
                size="sm"
                variant={deleteMode ? "outline" : "destructive"}
                onClick={() => setDeleteMode(!deleteMode)}
                className="flex items-center gap-2"
              >
                <Icon name={deleteMode ? "X" : "Trash2"} size={16} />
                {deleteMode ? "Отмена" : "Удалить по датам"}
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {deleteMode ? (
              <div className="bg-red-950/20 border border-red-900/50 rounded-lg p-4 space-y-4">
                <div className="flex items-center gap-2 text-red-400 mb-3">
                  <Icon name="AlertTriangle" size={20} />
                  <span className="font-semibold">Удаление диагностик по периоду</span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <div>
                    <label className="text-sm text-slate-400 block mb-1">Дата с:</label>
                    <Input
                      type="date"
                      value={deleteDateFrom}
                      onChange={(e) => setDeleteDateFrom(e.target.value)}
                      className="bg-slate-900 border-slate-700"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-slate-400 block mb-1">Дата по:</label>
                    <Input
                      type="date"
                      value={deleteDateTo}
                      onChange={(e) => setDeleteDateTo(e.target.value)}
                      className="bg-slate-900 border-slate-700"
                    />
                  </div>
                </div>
                <Button
                  variant="destructive"
                  onClick={deleteDiagnosticsByDateRange}
                  disabled={loading || !deleteDateFrom || !deleteDateTo}
                  className="w-full"
                >
                  <Icon name="Trash2" size={16} className="mr-2" />
                  Удалить диагностики за период
                </Button>
              </div>
            ) : (
              <>
                <div className="space-y-3">
                  <div className="flex gap-2">
                    <Input
                      placeholder="Поиск по гос.номеру или механику..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="bg-slate-900 border-slate-700 flex-1"
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={resetFilters}
                      title="Сбросить фильтры"
                    >
                      <Icon name="RotateCcw" size={16} />
                    </Button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3">
                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Механик:</label>
                      <Select value={filterMechanic} onValueChange={setFilterMechanic}>
                        <SelectTrigger className="bg-slate-900 border-slate-700">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Все механики</SelectItem>
                          {[...new Set(diagnostics.map(d => d.mechanic))].map(name => (
                            <SelectItem key={name} value={name}>{name}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Тип:</label>
                      <Select value={filterType} onValueChange={setFilterType}>
                        <SelectTrigger className="bg-slate-900 border-slate-700">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">Все типы</SelectItem>
                          {[...new Set(diagnostics.map(d => d.diagnosticType))].map(type => (
                            <SelectItem key={type} value={type}>{type}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Дата с:</label>
                      <Input
                        type="date"
                        value={dateFrom}
                        onChange={(e) => setDateFrom(e.target.value)}
                        className="bg-slate-900 border-slate-700"
                      />
                    </div>

                    <div>
                      <label className="text-xs text-slate-400 block mb-1">Дата по:</label>
                      <Input
                        type="date"
                        value={dateTo}
                        onChange={(e) => setDateTo(e.target.value)}
                        className="bg-slate-900 border-slate-700"
                      />
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  {filteredDiagnostics.length === 0 ? (
                    <div className="text-center py-8 text-slate-400">
                      <Icon name="Search" size={48} className="mx-auto mb-3 opacity-50" />
                      <p>Ничего не найдено</p>
                    </div>
                  ) : (
                    filteredDiagnostics.map((diagnostic) => (
                      <div key={diagnostic.id} className="bg-slate-900/50 rounded-lg p-4 border border-slate-700">
                        <div className="flex items-start justify-between gap-3">
                          <div className="flex-1 space-y-2">
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
                                {diagnostic.diagnosticType}
                              </Badge>
                              <span className="text-xs text-slate-500">
                                {new Date(diagnostic.createdAt).toLocaleString('ru-RU')}
                              </span>
                            </div>
                            <div className="text-sm text-slate-300">
                              <div>Механик: <span className="text-white font-medium">{diagnostic.mechanic}</span></div>
                              <div>Автомобиль: <span className="text-white font-medium">{diagnostic.carNumber}</span></div>
                              <div>Пробег: <span className="text-white font-medium">{diagnostic.mileage.toLocaleString()} км</span></div>
                            </div>
                          </div>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => deleteDiagnostic(diagnostic.id)}
                          >
                            <Icon name="Trash2" size={16} />
                          </Button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </>
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