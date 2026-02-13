import { useState, useEffect, useCallback, useRef } from 'react';

interface CacheEntry {
  data: any[];
  timestamp: number;
  etag?: string;
}

const CACHE_KEY = 'diagnostics_cache';
const CACHE_DURATION = 5 * 60 * 1000; // 5 минут

export const useCachedDiagnostics = () => {
  const [diagnostics, setDiagnostics] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);
  const cacheRef = useRef<CacheEntry | null>(null);

  const loadFromCache = useCallback(() => {
    try {
      const cached = localStorage.getItem(CACHE_KEY);
      if (cached) {
        const entry: CacheEntry = JSON.parse(cached);
        const age = Date.now() - entry.timestamp;
        
        if (age < CACHE_DURATION) {
          cacheRef.current = entry;
          setDiagnostics(entry.data);
          return true;
        } else {
          localStorage.removeItem(CACHE_KEY);
        }
      }
    } catch (err) {
      console.error('Cache read error:', err);
    }
    return false;
  }, []);

  const saveToCache = useCallback((data: any[], etag?: string) => {
    try {
      const entry: CacheEntry = {
        data,
        timestamp: Date.now(),
        etag
      };
      cacheRef.current = entry;
      localStorage.setItem(CACHE_KEY, JSON.stringify(entry));
    } catch (err) {
      console.error('Cache write error:', err);
    }
  }, []);

  const loadDiagnostics = useCallback(async (forceRefresh = false) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    if (!forceRefresh && loadFromCache()) {
      return;
    }

    setLoading(true);
    setError(null);
    
    abortControllerRef.current = new AbortController();

    try {
      const response = await fetch(
        'https://functions.poehali.dev/e76024e1-4735-4e57-bf5f-060276b574c8?limit=500',
        {
          signal: abortControllerRef.current.signal
        }
      );

      if (!response.ok) throw new Error('Ошибка загрузки');

      const data = await response.json();
      const etag = response.headers.get('ETag') || undefined;
      
      setDiagnostics(data);
      saveToCache(data, etag);
    } catch (err: any) { // eslint-disable-line @typescript-eslint/no-explicit-any
      if (err.name === 'AbortError') {
        return;
      }
      if (!loadFromCache()) {
        setError('Не удалось загрузить диагностики');
      }
      console.error('Fetch error:', err.message || err, 'for', 'https://functions.poehali.dev/e76024e1-4735-4e57-bf5f-060276b574c8?limit=500');
    } finally {
      setLoading(false);
    }
  }, [loadFromCache, saveToCache]);

  const invalidateCache = useCallback(() => {
    localStorage.removeItem(CACHE_KEY);
    cacheRef.current = null;
    loadDiagnostics(true);
  }, [loadDiagnostics]);

  useEffect(() => {
    loadDiagnostics();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const isCached = cacheRef.current !== null;
  const cacheAge = cacheRef.current 
    ? Date.now() - cacheRef.current.timestamp 
    : 0;

  return {
    diagnostics,
    loading,
    error,
    reload: invalidateCache,
    refresh: () => loadDiagnostics(true),
    isCached,
    cacheAge
  };
};