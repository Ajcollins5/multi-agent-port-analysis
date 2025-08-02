import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { debounce } from 'lodash';

interface NewsSnapshot {
  ticker: string;
  timestamp: string;
  category: string;
  impact: string;
  price_change_1h: number;
  price_change_24h: number;
  summary_line_1: string;
  summary_line_2: string;
  source_url: string;
  confidence_score: number;
}

interface OptimizedNewsDataOptions {
  ticker?: string;
  timeRange?: number;
  categoryFilter?: string;
  impactFilter?: string;
  searchQuery?: string;
  sortBy?: 'timestamp' | 'impact' | 'confidence';
  sortOrder?: 'asc' | 'desc';
  pageSize?: number;
  enableVirtualization?: boolean;
}

interface UseOptimizedNewsDataResult {
  newsHistory: NewsSnapshot[];
  filteredData: NewsSnapshot[];
  isLoading: boolean;
  error: string | null;
  totalCount: number;
  hasMore: boolean;
  loadMore: () => void;
  refresh: () => void;
  clearCache: () => void;
}

// OPTIMIZATION: Memoized filtering and sorting functions
const createFilterFunction = (
  searchQuery: string,
  categoryFilter: string,
  impactFilter: string,
  timeRange: number
) => {
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - timeRange);
  
  return (snapshot: NewsSnapshot): boolean => {
    // Time range filter
    if (new Date(snapshot.timestamp) < cutoffDate) return false;
    
    // Search filter
    if (searchQuery && !snapshot.summary_line_1.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !snapshot.summary_line_2.toLowerCase().includes(searchQuery.toLowerCase())) {
      return false;
    }
    
    // Category filter
    if (categoryFilter !== 'all' && snapshot.category !== categoryFilter) return false;
    
    // Impact filter
    if (impactFilter !== 'all' && snapshot.impact !== impactFilter) return false;
    
    return true;
  };
};

const createSortFunction = (sortBy: string, sortOrder: string) => {
  return (a: NewsSnapshot, b: NewsSnapshot): number => {
    let aValue: any, bValue: any;
    
    switch (sortBy) {
      case 'timestamp':
        aValue = new Date(a.timestamp).getTime();
        bValue = new Date(b.timestamp).getTime();
        break;
      case 'impact':
        aValue = Math.abs(a.price_change_24h);
        bValue = Math.abs(b.price_change_24h);
        break;
      case 'confidence':
        aValue = a.confidence_score;
        bValue = b.confidence_score;
        break;
      default:
        return 0;
    }
    
    const result = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
    return sortOrder === 'desc' ? -result : result;
  };
};

export const useOptimizedNewsData = (options: OptimizedNewsDataOptions = {}): UseOptimizedNewsDataResult => {
  const {
    ticker = 'AAPL',
    timeRange = 90,
    categoryFilter = 'all',
    impactFilter = 'all',
    searchQuery = '',
    sortBy = 'timestamp',
    sortOrder = 'desc',
    pageSize = 50,
    enableVirtualization = true
  } = options;

  const [newsHistory, setNewsHistory] = useState<NewsSnapshot[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(0);
  
  // OPTIMIZATION: Use refs to avoid unnecessary re-renders
  const cacheRef = useRef<Map<string, NewsSnapshot[]>>(new Map());
  const abortControllerRef = useRef<AbortController | null>(null);
  
  // OPTIMIZATION: Memoized filter function to prevent recreation on every render
  const filterFunction = useMemo(
    () => createFilterFunction(searchQuery, categoryFilter, impactFilter, timeRange),
    [searchQuery, categoryFilter, impactFilter, timeRange]
  );
  
  // OPTIMIZATION: Memoized sort function
  const sortFunction = useMemo(
    () => createSortFunction(sortBy, sortOrder),
    [sortBy, sortOrder]
  );
  
  // OPTIMIZATION: Memoized filtered and sorted data
  const filteredData = useMemo(() => {
    const filtered = newsHistory.filter(filterFunction);
    const sorted = [...filtered].sort(sortFunction);
    
    // Apply pagination for performance
    if (enableVirtualization) {
      return sorted.slice(0, (currentPage + 1) * pageSize);
    }
    
    return sorted;
  }, [newsHistory, filterFunction, sortFunction, currentPage, pageSize, enableVirtualization]);
  
  // OPTIMIZATION: Debounced data fetching to prevent excessive API calls
  const debouncedFetchData = useCallback(
    debounce(async (tickerToFetch: string) => {
      // Cancel previous request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      abortControllerRef.current = new AbortController();
      
      try {
        setIsLoading(true);
        setError(null);
        
        // Check cache first
        const cacheKey = `${tickerToFetch}_${timeRange}`;
        if (cacheRef.current.has(cacheKey)) {
          const cachedData = cacheRef.current.get(cacheKey)!;
          setNewsHistory(cachedData);
          setIsLoading(false);
          return;
        }
        
        const response = await fetch('/api/app_supabase', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            action: 'get_news_history',
            ticker: tickerToFetch,
            time_range_days: timeRange
          }),
          signal: abortControllerRef.current.signal
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
          const data = result.news_history || [];
          setNewsHistory(data);
          
          // Cache the result
          cacheRef.current.set(cacheKey, data);
          
          // OPTIMIZATION: Limit cache size to prevent memory leaks
          if (cacheRef.current.size > 10) {
            const firstKey = cacheRef.current.keys().next().value;
            cacheRef.current.delete(firstKey);
          }
        } else {
          throw new Error(result.error || 'Failed to fetch news data');
        }
      } catch (error: any) {
        if (error.name !== 'AbortError') {
          setError(error.message);
          console.error('Error fetching news data:', error);
        }
      } finally {
        setIsLoading(false);
      }
    }, 300), // 300ms debounce
    [timeRange]
  );
  
  // OPTIMIZATION: Effect with proper cleanup
  useEffect(() => {
    debouncedFetchData(ticker);
    
    return () => {
      // Cleanup on unmount
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      debouncedFetchData.cancel();
    };
  }, [ticker, debouncedFetchData]);
  
  // OPTIMIZATION: Memoized callbacks to prevent child re-renders
  const loadMore = useCallback(() => {
    setCurrentPage(prev => prev + 1);
  }, []);
  
  const refresh = useCallback(() => {
    const cacheKey = `${ticker}_${timeRange}`;
    cacheRef.current.delete(cacheKey);
    setCurrentPage(0);
    debouncedFetchData(ticker);
  }, [ticker, timeRange, debouncedFetchData]);
  
  const clearCache = useCallback(() => {
    cacheRef.current.clear();
    setCurrentPage(0);
  }, []);
  
  // OPTIMIZATION: Memoized computed values
  const totalCount = useMemo(() => {
    return newsHistory.filter(filterFunction).length;
  }, [newsHistory, filterFunction]);
  
  const hasMore = useMemo(() => {
    return enableVirtualization && filteredData.length < totalCount;
  }, [enableVirtualization, filteredData.length, totalCount]);
  
  return {
    newsHistory,
    filteredData,
    isLoading,
    error,
    totalCount,
    hasMore,
    loadMore,
    refresh,
    clearCache
  };
};

export default useOptimizedNewsData;
