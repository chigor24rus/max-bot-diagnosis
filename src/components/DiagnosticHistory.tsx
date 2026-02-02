import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

type Diagnostic = {
  id: number;
  mechanic: string;
  carNumber: string;
  mileage: number;
  diagnosticType: string;
  createdAt: string;
};

const diagnosticTypeLabels: Record<string, string> = {
  '5min': '5-ти минутка',
  'dhch': 'ДХЧ',
  'des': 'ДЭС'
};

const DiagnosticHistory = () => {
  const { toast } = useToast();
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedMechanic, setSelectedMechanic] = useState<string>('');
  const [generatingPdfId, setGeneratingPdfId] = useState<number | null>(null);

  useEffect(() => {
    loadDiagnostics();
  }, []);

  const loadDiagnostics = async () => {
    setLoading(true);
    try {
      const response = await fetch('https://functions.poehali.dev/e76024e1-4735-4e57-bf5f-060276b574c8?limit=100');
      
      if (!response.ok) {
        throw new Error('Ошибка загрузки');
      }
      
      const data = await response.json();
      setDiagnostics(data);
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить историю диагностик',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async (id: number) => {
    setGeneratingPdfId(id);
    try {
      const response = await fetch(`https://functions.poehali.dev/65879cb6-37f7-4a96-9bdc-04cfe5915ba6?id=${id}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Ошибка генерации');
      }
      
      const data = await response.json();
      
      if (!data.pdfUrl) {
        throw new Error('URL PDF не получен');
      }
      
      const newWindow = window.open(data.pdfUrl, '_blank');
      
      if (!newWindow) {
        toast({
          title: 'Внимание',
          description: 'Разрешите всплывающие окна для открытия PDF',
          variant: 'default'
        });
        window.location.href = data.pdfUrl;
        return;
      }
      
      toast({
        title: 'Готово!',
        description: 'PDF отчёт открыт в новой вкладке'
      });
    } catch (error) {
      console.error('PDF generation error:', error);
      toast({
        title: 'Ошибка',
        description: error instanceof Error ? error.message : 'Не удалось создать отчёт',
        variant: 'destructive'
      });
    } finally {
      setGeneratingPdfId(null);
    }
  };

  const filteredDiagnostics = diagnostics.filter(d => {
    const matchesSearch = 
      d.carNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      d.mechanic.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesMechanic = !selectedMechanic || d.mechanic === selectedMechanic;
    
    return matchesSearch && matchesMechanic;
  });

  const uniqueMechanics = Array.from(new Set(diagnostics.map(d => d.mechanic)));

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center space-y-3">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-slate-400">Загрузка истории...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <Card className="bg-slate-900/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <Icon name="History" size={24} className="text-primary" />
            История диагностик
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <Input
                placeholder="Поиск по госномеру или механику..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
              />
            </div>
            <div className="flex gap-2 flex-wrap">
              <Button
                variant={selectedMechanic === '' ? 'default' : 'outline'}
                onClick={() => setSelectedMechanic('')}
                size="sm"
                className={selectedMechanic === '' ? '' : 'bg-slate-800 border-slate-700 text-white hover:bg-slate-700'}
              >
                Все
              </Button>
              {uniqueMechanics.map(mechanic => (
                <Button
                  key={mechanic}
                  variant={selectedMechanic === mechanic ? 'default' : 'outline'}
                  onClick={() => setSelectedMechanic(mechanic)}
                  size="sm"
                  className={selectedMechanic === mechanic ? '' : 'bg-slate-800 border-slate-700 text-white hover:bg-slate-700'}
                >
                  {mechanic}
                </Button>
              ))}
            </div>
          </div>

          <div className="text-sm text-slate-400">
            Найдено: {filteredDiagnostics.length} из {diagnostics.length}
          </div>
        </CardContent>
      </Card>

      <div className="space-y-3">
        {filteredDiagnostics.length === 0 ? (
          <Card className="bg-slate-900/50 border-slate-700">
            <CardContent className="py-12 text-center">
              <Icon name="SearchX" size={48} className="text-slate-600 mx-auto mb-3" />
              <p className="text-slate-400">Диагностики не найдены</p>
            </CardContent>
          </Card>
        ) : (
          filteredDiagnostics.map((diagnostic) => (
            <Card key={diagnostic.id} className="bg-slate-900/50 border-slate-700 hover:border-primary/50 transition-all">
              <CardContent className="p-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="space-y-2 flex-1">
                    <div className="flex items-center gap-3 flex-wrap">
                      <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
                        №{diagnostic.id}
                      </Badge>
                      <Badge variant="outline" className="bg-accent/10 text-accent border-accent/30">
                        {diagnosticTypeLabels[diagnostic.diagnosticType] || diagnostic.diagnosticType}
                      </Badge>
                      <span className="text-xs text-slate-500">
                        {formatDate(diagnostic.createdAt)}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-sm">
                      <div className="flex items-center gap-2 text-slate-300">
                        <Icon name="Car" size={16} className="text-primary" />
                        <span className="font-semibold">{diagnostic.carNumber}</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <Icon name="Gauge" size={16} className="text-primary" />
                        <span>{diagnostic.mileage.toLocaleString('ru-RU')} км</span>
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <Icon name="User" size={16} className="text-primary" />
                        <span>{diagnostic.mechanic}</span>
                      </div>
                    </div>
                  </div>
                  
                  <Button
                    onClick={() => handleGenerateReport(diagnostic.id)}
                    variant="outline"
                    size="sm"
                    disabled={generatingPdfId === diagnostic.id}
                    className="bg-primary/10 hover:bg-primary/20 border-primary/30 text-primary hover:text-primary disabled:opacity-50"
                  >
                    {generatingPdfId === diagnostic.id ? (
                      <>
                        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin mr-2" />
                        Генерация...
                      </>
                    ) : (
                      <>
                        <Icon name="FileText" size={16} className="mr-2" />
                        PDF
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
};

export default DiagnosticHistory;