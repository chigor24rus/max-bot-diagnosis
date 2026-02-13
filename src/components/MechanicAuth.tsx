import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import Icon from '@/components/ui/icon';

type MechanicAuthProps = {
  onAuthenticated: (mechanic: { id: number; name: string }) => void;
};

const MechanicAuth = ({ onAuthenticated }: MechanicAuthProps) => {
  const [phone, setPhone] = useState('');
  const [pinCode, setPinCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const formatPhoneNumber = (value: string) => {
    // Удаляем все символы кроме цифр
    const cleaned = value.replace(/\D/g, '');
    
    // Форматируем в +7 (XXX) XXX-XX-XX
    if (cleaned.length === 0) return '';
    if (cleaned.length <= 1) return `+7`;
    if (cleaned.length <= 4) return `+7 (${cleaned.slice(1)}`;
    if (cleaned.length <= 7) return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4)}`;
    if (cleaned.length <= 9) return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
    return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7, 9)}-${cleaned.slice(9, 11)}`;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatPhoneNumber(e.target.value);
    setPhone(formatted);
    setError('');
  };

  const handlePinChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/\D/g, '').slice(0, 4);
    setPinCode(value);
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!phone || !pinCode) {
      setError('Заполните все поля');
      return;
    }

    if (pinCode.length !== 4) {
      setError('Пин-код должен состоять из 4 цифр');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      const cleanPhone = phone.replace(/\D/g, '');
      const formattedPhone = `+${cleanPhone}`;

      const response = await fetch('https://functions.poehali.dev/b75c9b1a-314a-4add-aa18-6661d2618427', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: formattedPhone,
          pin_code: pinCode,
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        // Сохраняем данные в localStorage
        localStorage.setItem('mechanic_id', data.mechanic.id.toString());
        localStorage.setItem('mechanic_name', data.mechanic.name);
        
        onAuthenticated(data.mechanic);
      } else {
        setError(data.error || 'Неверный номер телефона или пин-код');
      }
    } catch (err) {
      console.error('Auth error:', err);
      setError('Ошибка подключения к серверу');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-3 sm:p-4 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Card className="w-full max-w-md bg-slate-950/90 border-primary/20">
        <CardHeader className="text-center p-4 sm:p-6">
          <div className="flex justify-center mb-3 sm:mb-4">
            <div className="p-3 sm:p-4 bg-primary/10 rounded-full">
              <Icon name="Lock" size={40} className="text-primary sm:w-12 sm:h-12" />
            </div>
          </div>
          <CardTitle className="text-xl sm:text-2xl text-white">Авторизация</CardTitle>
          <CardDescription className="text-slate-400 text-sm">
            HEVSR Diagnostics — вход для механиков
          </CardDescription>
        </CardHeader>
        <CardContent className="p-4 sm:p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="phone" className="text-slate-300">
                Номер телефона
              </Label>
              <div className="relative">
                <Icon 
                  name="Phone" 
                  size={18} 
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" 
                />
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+7 (___) ___-__-__"
                  value={phone}
                  onChange={handlePhoneChange}
                  className="pl-10 bg-slate-900/50 border-slate-700 text-white"
                  disabled={isLoading}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="pinCode" className="text-slate-300">
                Пин-код (4 цифры)
              </Label>
              <div className="relative">
                <Icon 
                  name="KeyRound" 
                  size={18} 
                  className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" 
                />
                <Input
                  id="pinCode"
                  type="password"
                  inputMode="numeric"
                  placeholder="••••"
                  value={pinCode}
                  onChange={handlePinChange}
                  maxLength={4}
                  className="pl-10 bg-slate-900/50 border-slate-700 text-white text-center text-2xl tracking-widest"
                  disabled={isLoading}
                />
              </div>
            </div>

            {error && (
              <div className="flex items-center gap-2 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                <Icon name="AlertCircle" size={18} className="text-red-400 flex-shrink-0" />
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading || !phone || pinCode.length !== 4}
            >
              {isLoading ? (
                <>
                  <Icon name="Loader2" size={18} className="mr-2 animate-spin" />
                  Проверка...
                </>
              ) : (
                <>
                  <Icon name="LogIn" size={18} className="mr-2" />
                  Войти
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-700">
            <p className="text-sm text-slate-400 text-center">
              Нет доступа? Обратитесь к администратору для получения учётных данных.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MechanicAuth;