import { useState, useEffect, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Icon from '@/components/ui/icon';
import { useToast } from '@/hooks/use-toast';
import { useDebounce } from '@/hooks/useDebounce';

interface DiagnosticsManagerProps {
  diagnostics: any[];
  onReload: () => void;
  loading?: boolean;
  isCached?: boolean;
  cacheAge?: number;
}

const DiagnosticsManager = ({ 
  diagnostics, 
  onReload, 
  loading: externalLoading,
  isCached,
  cacheAge
}: DiagnosticsManagerProps) => {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterMechanic, setFilterMechanic] = useState('all');
  const [filterType, setFilterType] = useState('all');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [deleteMode, setDeleteMode] = useState(false);
  const [deleteDateFrom, setDeleteDateFrom] = useState('');
  const [deleteDateTo, setDeleteDateTo] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(50);

  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  const filteredDiagnostics = useMemo(() => {
    let filtered = [...diagnostics];

    if (debouncedSearchQuery) {
      const query = debouncedSearchQuery.toLowerCase();
      filtered = filtered.filter(d => 
        d.carNumber.toLowerCase().includes(query) ||
        d.mechanic.toLowerCase().includes(query)
      );
    }

    if (filterMechanic !== 'all') {
      filtered = filtered.filter(d => d.mechanic === filterMechanic);
    }

    if (filterType !== 'all') {
      filtered = filtered.filter(d => d.diagnosticType === filterType);
    }

    if (dateFrom) {
      const startDate = new Date(dateFrom);
      filtered = filtered.filter(d => new Date(d.createdAt) >= startDate);
    }

    if (dateTo) {
      const endDate = new Date(dateTo);
      endDate.setHours(23, 59, 59, 999);
      filtered = filtered.filter(d => new Date(d.createdAt) <= endDate);
    }

    return filtered;
  }, [diagnostics, debouncedSearchQuery, filterMechanic, filterType, dateFrom, dateTo]);

  const paginatedDiagnostics = useMemo(() => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredDiagnostics.slice(startIndex, endIndex);
  }, [filteredDiagnostics, currentPage, itemsPerPage]);

  const totalPages = Math.ceil(filteredDiagnostics.length / itemsPerPage);

  useEffect(() => {
    setCurrentPage(1);
  }, [debouncedSearchQuery, filterMechanic, filterType, dateFrom, dateTo]);

  const deleteDiagnostic = async (id: number) => {
    try {
      const response = await fetch(`https://functions.poehali.dev/e76024e1-4735-4e57-bf5f-060276b574c8?id=${id}`, {
        method: 'DELETE'
      });
      
      if (!response.ok) throw new Error('Ошибка удаления');
      
      toast({ title: 'Готово', description: 'Диагностика удалена' });
      onReload();
    } catch (error) {
      toast({ title: 'Ошибка', description: 'Не удалось удалить диагностику', variant: 'destructive' });
    }
  };

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
    onReload();
  };

  const resetFilters = () => {
    setSearchQuery('');
    setFilterMechanic('all');
    setFilterType('all');
    setDateFrom('');
    setDateTo('');
    setCurrentPage(1);
  };

  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <Card className="bg-slate-950/90 border-slate-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-white flex items-center gap-2">
              <Icon name="ClipboardList" size={20} className="text-primary" />
              Диагностики
              {externalLoading ? (
                <Icon name="Loader2" size={16} className="animate-spin text-primary ml-2" />
              ) : (
                <>
                  <Badge variant="outline" className="ml-2">{filteredDiagnostics.length}</Badge>
                  {diagnostics.length > 1000 && (
                    <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/30">
                      Оптимизировано
                    </Badge>
                  )}
                  {isCached && cacheAge && cacheAge < 300000 && (
                    <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/30">
                      <Icon name="Database" size={12} className="mr-1" />
                      Кеш
                    </Badge>
                  )}
                </>
              )}
            </CardTitle>
            <CardDescription>
              История сохранённых диагностик
              {diagnostics.length !== filteredDiagnostics.length && (
                <span className="text-primary ml-2">
                  (отфильтровано из {diagnostics.length})
                </span>
              )}
              {isCached && cacheAge && (
                <span className="text-slate-500 ml-2">
                  • обновлено {Math.floor(cacheAge / 1000)}с назад
                </span>
              )}
            </CardDescription>
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
                <>
                  <div className="flex items-center justify-between text-sm text-slate-400 mb-2">
                    <div>
                      Показано {((currentPage - 1) * itemsPerPage) + 1} - {Math.min(currentPage * itemsPerPage, filteredDiagnostics.length)} из {filteredDiagnostics.length}
                    </div>
                    <Select value={itemsPerPage.toString()} onValueChange={(v) => { setItemsPerPage(Number(v)); setCurrentPage(1); }}>
                      <SelectTrigger className="w-32 h-8 bg-slate-900 border-slate-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="25">25 на странице</SelectItem>
                        <SelectItem value="50">50 на странице</SelectItem>
                        <SelectItem value="100">100 на странице</SelectItem>
                        <SelectItem value="200">200 на странице</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {paginatedDiagnostics.map((diagnostic) => (
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
                  ))}
                  {totalPages > 1 && (
                    <div className="flex items-center justify-center gap-2 mt-4 pt-4 border-t border-slate-700">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => goToPage(1)}
                        disabled={currentPage === 1}
                      >
                        <Icon name="ChevronsLeft" size={16} />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => goToPage(currentPage - 1)}
                        disabled={currentPage === 1}
                      >
                        <Icon name="ChevronLeft" size={16} />
                      </Button>
                      <div className="flex items-center gap-2 text-sm text-slate-300">
                        <span>Страница</span>
                        <Input
                          type="number"
                          min="1"
                          max={totalPages}
                          value={currentPage}
                          onChange={(e) => {
                            const page = parseInt(e.target.value);
                            if (page >= 1 && page <= totalPages) {
                              setCurrentPage(page);
                            }
                          }}
                          className="w-16 h-8 text-center bg-slate-900 border-slate-700"
                        />
                        <span>из {totalPages}</span>
                      </div>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => goToPage(currentPage + 1)}
                        disabled={currentPage === totalPages}
                      >
                        <Icon name="ChevronRight" size={16} />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => goToPage(totalPages)}
                        disabled={currentPage === totalPages}
                      >
                        <Icon name="ChevronsRight" size={16} />
                      </Button>
                    </div>
                  )}
                </>
              )}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default DiagnosticsManager;