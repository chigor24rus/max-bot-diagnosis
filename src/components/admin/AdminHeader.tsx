import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import Icon from '@/components/ui/icon';

interface AdminHeaderProps {
  onLogout: () => void;
}

const AdminHeader = ({ onLogout }: AdminHeaderProps) => {
  return (
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
            onClick={onLogout}
            className="flex items-center gap-2"
          >
            <Icon name="LogOut" size={16} />
            Выйти
          </Button>
        </div>
      </CardHeader>
    </Card>
  );
};

export default AdminHeader;
