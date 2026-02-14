import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';

type StorageData = {
  totalSize: number;
  totalSizeFormatted: string;
  totalFiles: number;
  photos: { size: number; sizeFormatted: string; count: number };
  reports: { size: number; sizeFormatted: string; count: number };
  other: { size: number; sizeFormatted: string; count: number };
};

type CleanupResult = {
  dryRun: boolean;
  orphanFiles: number;
  orphanSize: number;
  orphanSizeFormatted: string;
  deletedFiles: number;
  keptFiles: number;
  keptSizeFormatted: string;
};

const STORAGE_URL = 'https://functions.poehali.dev/e1bacd58-95dc-4051-ae23-ee4fefa08c66';
const CLEANUP_URL = 'https://functions.poehali.dev/2698715e-5a7c-43d5-bc62-78b8d2a798c6';

const StorageInfo = () => {
  const { toast } = useToast();
  const [data, setData] = useState<StorageData | null>(null);
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [scanResult, setScanResult] = useState<CleanupResult | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const response = await fetch(STORAGE_URL);
      if (response.ok) {
        setData(await response.json());
      }
    } catch (e) {
      console.error('Storage load error:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const scanOrphans = async () => {
    setScanning(true);
    setScanResult(null);
    try {
      const response = await fetch(CLEANUP_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dryRun: true })
      });
      if (response.ok) {
        const result: CleanupResult = await response.json();
        setScanResult(result);
        if (result.orphanFiles === 0) {
          toast({ title: 'Всё чисто', description: 'Ненужных файлов не найдено' });
        }
      }
    } catch (e) {
      console.error('Scan error:', e);
      toast({ title: 'Ошибка', description: 'Не удалось выполнить сканирование', variant: 'destructive' });
    } finally {
      setScanning(false);
    }
  };

  const performCleanup = async () => {
    if (!confirm(`Удалить ${scanResult?.orphanFiles} ненужных файлов (${scanResult?.orphanSizeFormatted})? Это действие необратимо.`)) {
      return;
    }
    setCleaning(true);
    try {
      const response = await fetch(CLEANUP_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dryRun: false })
      });
      if (response.ok) {
        const result: CleanupResult = await response.json();
        toast({
          title: 'Очистка завершена',
          description: `Удалено ${result.deletedFiles} файлов`
        });
        setScanResult(null);
        loadData();
      }
    } catch (e) {
      console.error('Cleanup error:', e);
      toast({ title: 'Ошибка', description: 'Не удалось выполнить очистку', variant: 'destructive' });
    } finally {
      setCleaning(false);
    }
  };

  const getPercentage = (part: number, total: number) => {
    if (total === 0) return 0;
    return Math.round((part / total) * 100);
  };

  return (
    <Card className="bg-slate-950/90 border-slate-700">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-white flex items-center gap-2 text-base">
            <Icon name="HardDrive" size={20} className="text-primary" />
            Хранилище файлов
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              onClick={loadData}
              disabled={loading}
              className="h-8 w-8 p-0"
            >
              <Icon name="RefreshCw" size={14} className={loading ? 'animate-spin' : ''} />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading && !data ? (
          <div className="flex items-center justify-center py-6">
            <Icon name="Loader2" size={20} className="animate-spin text-primary" />
          </div>
        ) : data ? (
          <div className="space-y-4">
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold text-white">{data.totalSizeFormatted}</span>
              <span className="text-sm text-slate-400">/ {data.totalFiles} файлов</span>
            </div>

            <div className="w-full h-3 bg-slate-800 rounded-full overflow-hidden flex">
              {data.totalSize > 0 && (
                <>
                  <div
                    className="h-full bg-blue-500"
                    style={{ width: `${getPercentage(data.photos.size, data.totalSize)}%` }}
                    title={`Фото: ${data.photos.sizeFormatted}`}
                  />
                  <div
                    className="h-full bg-emerald-500"
                    style={{ width: `${getPercentage(data.reports.size, data.totalSize)}%` }}
                    title={`Отчёты: ${data.reports.sizeFormatted}`}
                  />
                  {data.other.size > 0 && (
                    <div
                      className="h-full bg-slate-500"
                      style={{ width: `${getPercentage(data.other.size, data.totalSize)}%` }}
                      title={`Прочее: ${data.other.sizeFormatted}`}
                    />
                  )}
                </>
              )}
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                  <span className="text-xs text-slate-400">Фото</span>
                </div>
                <div className="text-sm font-semibold text-white">{data.photos.sizeFormatted}</div>
                <div className="text-xs text-slate-500">{data.photos.count} файлов</div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  <span className="text-xs text-slate-400">Отчёты</span>
                </div>
                <div className="text-sm font-semibold text-white">{data.reports.sizeFormatted}</div>
                <div className="text-xs text-slate-500">{data.reports.count} файлов</div>
              </div>

              <div className="bg-slate-900/50 rounded-lg p-3 border border-slate-800">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2.5 h-2.5 rounded-full bg-slate-500" />
                  <span className="text-xs text-slate-400">Прочее</span>
                </div>
                <div className="text-sm font-semibold text-white">{data.other.sizeFormatted}</div>
                <div className="text-xs text-slate-500">{data.other.count} файлов</div>
              </div>
            </div>

            {scanResult && scanResult.orphanFiles > 0 && (
              <div className="bg-amber-950/30 border border-amber-700/40 rounded-lg p-3 space-y-3">
                <div className="flex items-center gap-2 text-amber-400 text-sm font-medium">
                  <Icon name="AlertTriangle" size={16} />
                  Найдено {scanResult.orphanFiles} ненужных файлов ({scanResult.orphanSizeFormatted})
                </div>
                <p className="text-xs text-slate-400">
                  Это файлы от удалённых диагностик, которые остались в хранилище.
                </p>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={performCleanup}
                  disabled={cleaning}
                  className="w-full"
                >
                  {cleaning ? (
                    <>
                      <Icon name="Loader2" size={14} className="animate-spin mr-2" />
                      Удаление...
                    </>
                  ) : (
                    <>
                      <Icon name="Trash2" size={14} className="mr-2" />
                      Удалить ненужные файлы
                    </>
                  )}
                </Button>
              </div>
            )}

            <Button
              size="sm"
              variant="outline"
              onClick={scanOrphans}
              disabled={scanning || cleaning}
              className="w-full border-slate-700 text-slate-300 hover:text-white"
            >
              {scanning ? (
                <>
                  <Icon name="Loader2" size={14} className="animate-spin mr-2" />
                  Сканирование...
                </>
              ) : (
                <>
                  <Icon name="Search" size={14} className="mr-2" />
                  Найти ненужные файлы
                </>
              )}
            </Button>
          </div>
        ) : (
          <div className="text-center py-4 text-slate-500 text-sm">
            Не удалось загрузить данные
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default StorageInfo;
