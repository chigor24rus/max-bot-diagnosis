import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useCachedDiagnostics } from '@/hooks/useCachedDiagnostics';
import AdminHeader from '@/components/admin/AdminHeader';
import WebhookManager from '@/components/admin/WebhookManager';
import DiagnosticsManager from '@/components/admin/DiagnosticsManager';
import AdminInstructions from '@/components/admin/AdminInstructions';
import MechanicsManager from '@/components/MechanicsManager';

const Admin = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { diagnostics, loading, error, reload, isCached, cacheAge } = useCachedDiagnostics();

  const webhookUrl = 'https://functions.poehali.dev/f48b0eea-37b1-4cf5-a470-aa20ae0fd775';
  const setupUrl = 'https://functions.poehali.dev/8e7d060d-23fb-4628-88e9-e251279d6a28';

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    if (!token) {
      navigate('/login');
    }
  }, [navigate]);

  useEffect(() => {
    if (error) {
      toast({ title: 'Ошибка', description: error, variant: 'destructive' });
    }
  }, [error, toast]);

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    toast({ title: 'Выход выполнен' });
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        <AdminHeader onLogout={handleLogout} />
        <WebhookManager webhookUrl={webhookUrl} setupUrl={setupUrl} />
        <MechanicsManager />
        <DiagnosticsManager 
          diagnostics={diagnostics} 
          onReload={reload}
          loading={loading}
          isCached={isCached}
          cacheAge={cacheAge}
        />
        <AdminInstructions />
      </div>
    </div>
  );
};

export default Admin;