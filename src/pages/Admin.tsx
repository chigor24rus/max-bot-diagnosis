import { useEffect, Component, ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from '@/hooks/use-toast';
import { useCachedDiagnostics } from '@/hooks/useCachedDiagnostics';
import AdminHeader from '@/components/admin/AdminHeader';
import WebhookManager from '@/components/admin/WebhookManager';
import DiagnosticsManager from '@/components/admin/DiagnosticsManager';
import AdminInstructions from '@/components/admin/AdminInstructions';
import StorageInfo from '@/components/admin/StorageInfo';
import MechanicsManager from '@/components/MechanicsManager';

class AdminErrorBoundary extends Component<{children: ReactNode}, {hasError: boolean; error: string}> {
  constructor(props: {children: ReactNode}) {
    super(props);
    this.state = { hasError: false, error: '' };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('Admin page error:', error, info);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <div className="bg-red-950/50 border border-red-500/30 rounded-lg p-6 max-w-md text-center">
            <h2 className="text-red-400 text-xl font-bold mb-2">Ошибка загрузки</h2>
            <p className="text-slate-300 mb-4">{this.state.error}</p>
            <button onClick={() => window.location.reload()} className="bg-primary text-white px-4 py-2 rounded">
              Перезагрузить
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

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
  }, [error]); // eslint-disable-line react-hooks/exhaustive-deps

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
        <StorageInfo />
        <AdminErrorBoundary>
          <DiagnosticsManager 
            diagnostics={diagnostics} 
            onReload={reload}
            loading={loading}
            isCached={isCached}
            cacheAge={cacheAge}
          />
        </AdminErrorBoundary>
        <AdminInstructions />
      </div>
    </div>
  );
};

const AdminWithBoundary = () => (
  <AdminErrorBoundary>
    <Admin />
  </AdminErrorBoundary>
);

export default AdminWithBoundary;