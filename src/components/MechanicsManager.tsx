import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

type Mechanic = {
  id: number;
  name: string;
  phone: string;
  pinCode: string;
  isActive: boolean;
  createdAt: string;
};

const MechanicsManager = () => {
  const { toast } = useToast();
  const [mechanics, setMechanics] = useState<Mechanic[]>([]);
  const [loading, setLoading] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingMechanic, setEditingMechanic] = useState<Mechanic | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    pinCode: '',
  });

  const mechanicsApiUrl = 'https://functions.poehali.dev/47f92079-1392-4766-911a-8aa94a4d8db9';

  useEffect(() => {
    loadMechanics();
  }, []);

  const loadMechanics = async () => {
    setLoading(true);
    try {
      const response = await fetch(mechanicsApiUrl);
      if (!response.ok) throw new Error('Ошибка загрузки');

      const data = await response.json();
      setMechanics(data);
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить список механиков',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const formatPhoneNumber = (value: string) => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length === 0) return '';
    if (cleaned.length <= 1) return `+7`;
    if (cleaned.length <= 4) return `+7 (${cleaned.slice(1)}`;
    if (cleaned.length <= 7) return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4)}`;
    if (cleaned.length <= 9)
      return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
    return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7, 9)}-${cleaned.slice(9, 11)}`;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhoneNumber(e.target.value);
    setFormData({ ...formData, phone: formatted });
  };

  const handlePinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 4);
    setFormData({ ...formData, pinCode: value });
  };

  const handleOpenDialog = (mechanic?: Mechanic) => {
    if (mechanic) {
      setEditingMechanic(mechanic);
      setFormData({
        name: mechanic.name,
        phone: mechanic.phone,
        pinCode: mechanic.pinCode,
      });
    } else {
      setEditingMechanic(null);
      setFormData({ name: '', phone: '', pinCode: '' });
    }
    setIsDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name || !formData.phone || formData.pinCode.length !== 4) {
      toast({
        title: 'Ошибка',
        description: 'Заполните все поля корректно',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      const method = editingMechanic ? 'PUT' : 'POST';
      const body = editingMechanic
        ? { id: editingMechanic.id, ...formData }
        : formData;

      const response = await fetch(mechanicsApiUrl, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!response.ok) throw new Error('Ошибка сохранения');

      toast({
        title: 'Успешно',
        description: editingMechanic ? 'Механик обновлён' : 'Механик добавлен',
      });

      setIsDialogOpen(false);
      loadMechanics();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось сохранить механика',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleToggleActive = async (mechanic: Mechanic) => {
    setLoading(true);
    try {
      const response = await fetch(mechanicsApiUrl, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: mechanic.id,
          isActive: !mechanic.isActive,
        }),
      });

      if (!response.ok) throw new Error('Ошибка обновления');

      toast({
        title: 'Успешно',
        description: mechanic.isActive ? 'Механик деактивирован' : 'Механик активирован',
      });

      loadMechanics();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось обновить статус',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены, что хотите удалить механика?')) return;

    setLoading(true);
    try {
      const response = await fetch(`${mechanicsApiUrl}?id=${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error('Ошибка удаления');

      toast({
        title: 'Успешно',
        description: 'Механик удалён',
      });

      loadMechanics();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось удалить механика',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="bg-slate-950/90 border-primary/20">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-white">Управление механиками</CardTitle>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => handleOpenDialog()}>
              <Icon name="Plus" size={18} className="mr-2" />
              Добавить механика
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-slate-950 border-primary/20">
            <DialogHeader>
              <DialogTitle className="text-white">
                {editingMechanic ? 'Редактировать механика' : 'Добавить механика'}
              </DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name" className="text-slate-300">
                  ФИО
                </Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="Иванов И.И."
                  className="bg-slate-900/50 border-slate-700 text-white"
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone" className="text-slate-300">
                  Номер телефона
                </Label>
                <Input
                  id="phone"
                  type="tel"
                  value={formData.phone}
                  onChange={handlePhoneChange}
                  placeholder="+7 (___) ___-__-__"
                  className="bg-slate-900/50 border-slate-700 text-white"
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="pinCode" className="text-slate-300">
                  Пин-код (4 цифры)
                </Label>
                <Input
                  id="pinCode"
                  type="password"
                  inputMode="numeric"
                  value={formData.pinCode}
                  onChange={handlePinChange}
                  placeholder="••••"
                  maxLength={4}
                  className="bg-slate-900/50 border-slate-700 text-white text-center text-xl tracking-widest"
                  disabled={loading}
                />
              </div>

              <div className="flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsDialogOpen(false)}
                  disabled={loading}
                >
                  Отмена
                </Button>
                <Button type="submit" disabled={loading}>
                  {loading ? 'Сохранение...' : 'Сохранить'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </CardHeader>

      <CardContent>
        {loading && mechanics.length === 0 ? (
          <div className="text-center py-8 text-slate-400">Загрузка...</div>
        ) : mechanics.length === 0 ? (
          <div className="text-center py-8 text-slate-400">Нет механиков</div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="border-slate-700">
                <TableHead className="text-slate-300">ФИО</TableHead>
                <TableHead className="text-slate-300">Телефон</TableHead>
                <TableHead className="text-slate-300">Пин-код</TableHead>
                <TableHead className="text-slate-300">Статус</TableHead>
                <TableHead className="text-slate-300 text-right">Действия</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {mechanics.map((mechanic) => (
                <TableRow key={mechanic.id} className="border-slate-700">
                  <TableCell className="text-white">{mechanic.name}</TableCell>
                  <TableCell className="text-slate-300">{mechanic.phone}</TableCell>
                  <TableCell className="text-slate-300">
                    <code className="text-sm">{'•'.repeat(4)}</code>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={mechanic.isActive ? 'default' : 'secondary'}
                      className={mechanic.isActive ? 'bg-green-500/20 text-green-400' : ''}
                    >
                      {mechanic.isActive ? 'Активен' : 'Неактивен'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleOpenDialog(mechanic)}
                        disabled={loading}
                      >
                        <Icon name="Pencil" size={16} />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleToggleActive(mechanic)}
                        disabled={loading}
                      >
                        <Icon name={mechanic.isActive ? 'Ban' : 'Check'} size={16} />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDelete(mechanic.id)}
                        disabled={loading}
                        className="text-red-400 hover:text-red-300"
                      >
                        <Icon name="Trash2" size={16} />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
};

export default MechanicsManager;
