// Note: Install @tanstack/react-query before using this hook
// npm install @tanstack/react-query
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useRef, useCallback } from 'react';

export interface PollingConfig {
  interval: number;
  enabled: boolean;
  maxRetries?: number;
  retryDelay?: number;
  staleTime?: number;
}

export interface PollingResult<T> {
  data: T | undefined;
  isLoading: boolean;
  error: Error | null;
  isPolling: boolean;
  startPolling: () => void;
  stopPolling: () => void;
  refetch: () => void;
  updateInterval: (newInterval: number) => void;
}

/**
 * Hook for real-time polling to replace Streamlit's WebSocket functionality
 * Provides intelligent polling with automatic retry, error handling, and performance optimization
 */
export function useRealTimePolling<T>(
  queryKey: string[],
  queryFn: () => Promise<T>,
  config: PollingConfig = {
    interval: 5000,
    enabled: false,
    maxRetries: 3,
    retryDelay: 1000,
    staleTime: 1000
  }
): PollingResult<T> {
  const [isPolling, setIsPolling] = useState(config.enabled);
  const [currentInterval, setCurrentInterval] = useState(config.interval);
  const retryCountRef = useRef(0);
  const queryClient = useQueryClient();

  // React Query setup with polling
  const query = useQuery({
    queryKey,
    queryFn: async () => {
      try {
        const result = await queryFn();
        retryCountRef.current = 0; // Reset retry count on success
        return result;
      } catch (error) {
        retryCountRef.current += 1;
        throw error;
      }
    },
    refetchInterval: isPolling ? currentInterval : false,
    refetchIntervalInBackground: true,
    refetchOnWindowFocus: true,
    staleTime: config.staleTime || 1000,
    retry: (failureCount: number, error: unknown) => {
      if (failureCount >= (config.maxRetries || 3)) {
        return false;
      }
      // Exponential backoff for retries
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey });
      }, (config.retryDelay || 1000) * Math.pow(2, failureCount));
      return true;
    },
    enabled: isPolling,
  });

  // Start polling
  const startPolling = useCallback(() => {
    setIsPolling(true);
    retryCountRef.current = 0;
  }, []);

  // Stop polling
  const stopPolling = useCallback(() => {
    setIsPolling(false);
  }, []);

  // Update polling interval
  const updateInterval = useCallback((newInterval: number) => {
    setCurrentInterval(newInterval);
  }, []);

  // Manual refetch
  const refetch = useCallback(() => {
    query.refetch();
  }, [query]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      setIsPolling(false);
    };
  }, []);

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    isPolling,
    startPolling,
    stopPolling,
    refetch,
    updateInterval,
  };
}

/**
 * Hook for polling portfolio data with smart caching
 */
export function usePortfolioPolling(interval: number = 30000) {
  return useRealTimePolling(
    ['portfolio', 'data'],
    async () => {
      const response = await fetch('/api/supervisor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'analyze_portfolio' })
      });
      
      if (!response.ok) {
        throw new Error(`Portfolio analysis failed: ${response.status}`);
      }
      
      return response.json();
    },
    {
      interval,
      enabled: false,
      maxRetries: 3,
      retryDelay: 2000,
      staleTime: 10000 // 10 seconds
    }
  );
}

/**
 * Hook for polling event data
 */
export function useEventPolling(interval: number = 5000) {
  return useRealTimePolling(
    ['events', 'stream'],
    async () => {
      const response = await fetch('/api/agents/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'detect_events' })
      });
      
      if (!response.ok) {
        throw new Error(`Event detection failed: ${response.status}`);
      }
      
      return response.json();
    },
    {
      interval,
      enabled: false,
      maxRetries: 5,
      retryDelay: 1000,
      staleTime: 2000 // 2 seconds for events
    }
  );
}

/**
 * Hook for polling stock analysis data
 */
export function useStockAnalysisPolling(ticker: string, interval: number = 15000) {
  return useRealTimePolling(
    ['stock', 'analysis', ticker],
    async () => {
      const response = await fetch('/api/supervisor', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          action: 'analyze_ticker', 
          ticker: ticker.toUpperCase() 
        })
      });
      
      if (!response.ok) {
        throw new Error(`Stock analysis failed: ${response.status}`);
      }
      
      return response.json();
    },
    {
      interval,
      enabled: false,
      maxRetries: 3,
      retryDelay: 2000,
      staleTime: 5000 // 5 seconds
    }
  );
}

/**
 * Hook for polling insights data
 */
export function useInsightsPolling(interval: number = 20000) {
  return useRealTimePolling(
    ['insights', 'latest'],
    async () => {
      const response = await fetch('/api/storage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'get_insights', limit: 10 })
      });
      
      if (!response.ok) {
        throw new Error(`Insights fetch failed: ${response.status}`);
      }
      
      return response.json();
    },
    {
      interval,
      enabled: false,
      maxRetries: 3,
      retryDelay: 3000,
      staleTime: 15000 // 15 seconds
    }
  );
}

/**
 * Hook for polling system status
 */
export function useSystemStatusPolling(interval: number = 60000) {
  return useRealTimePolling(
    ['system', 'status'],
    async () => {
      const response = await fetch('/api/health', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) {
        throw new Error(`System status check failed: ${response.status}`);
      }
      
      return response.json();
    },
    {
      interval,
      enabled: false,
      maxRetries: 5,
      retryDelay: 5000,
      staleTime: 30000 // 30 seconds
    }
  );
}

/**
 * Hook for adaptive polling based on user activity
 */
export function useAdaptivePolling<T>(
  queryKey: string[],
  queryFn: () => Promise<T>,
  baseInterval: number = 5000
): PollingResult<T> {
  const [isActive, setIsActive] = useState(true);
  const [adaptiveInterval, setAdaptiveInterval] = useState(baseInterval);

  // Listen for user activity
  useEffect(() => {
    const handleActivity = () => {
      setIsActive(true);
      setAdaptiveInterval(baseInterval);
    };

    const handleInactivity = () => {
      setIsActive(false);
      setAdaptiveInterval(baseInterval * 3); // Slower polling when inactive
    };

    // Set up activity detection
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];
    let inactivityTimer: NodeJS.Timeout;

    const resetInactivityTimer = () => {
      clearTimeout(inactivityTimer);
      handleActivity();
      inactivityTimer = setTimeout(handleInactivity, 60000); // 1 minute of inactivity
    };

    events.forEach(event => {
      document.addEventListener(event, resetInactivityTimer, true);
    });

    resetInactivityTimer();

    return () => {
      events.forEach(event => {
        document.removeEventListener(event, resetInactivityTimer, true);
      });
      clearTimeout(inactivityTimer);
    };
  }, [baseInterval]);

  return useRealTimePolling(
    queryKey,
    queryFn,
    {
      interval: adaptiveInterval,
      enabled: false,
      maxRetries: 3,
      retryDelay: 2000,
      staleTime: isActive ? 1000 : 5000
    }
  );
}

/**
 * Hook for batch polling multiple queries
 */
export function useBatchPolling(
  queries: Array<{
    queryKey: string[];
    queryFn: () => Promise<any>;
    interval?: number;
  }>,
  globalInterval: number = 10000
) {
  const [isPolling, setIsPolling] = useState(false);
  
  const results = queries.map(query => {
    return useRealTimePolling(
      query.queryKey,
      query.queryFn,
      {
        interval: query.interval || globalInterval,
        enabled: isPolling,
        maxRetries: 3,
        retryDelay: 1000,
        staleTime: 2000
      }
    );
  });

  const startPolling = useCallback(() => {
    setIsPolling(true);
    results.forEach(result => result.startPolling());
  }, [results]);

  const stopPolling = useCallback(() => {
    setIsPolling(false);
    results.forEach(result => result.stopPolling());
  }, [results]);

  const refetchAll = useCallback(() => {
    results.forEach(result => result.refetch());
  }, [results]);

  return {
    results,
    isPolling,
    startPolling,
    stopPolling,
    refetchAll,
  };
}

/**
 * Hook for WebSocket-like updates using Server-Sent Events
 */
export function useServerSentEvents(url: string, enabled: boolean = false) {
  const [data, setData] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!enabled) {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
        setIsConnected(false);
      }
      return;
    }

    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const parsedData = JSON.parse(event.data);
        setData(parsedData);
      } catch (e) {
        setData(event.data);
      }
    };

    eventSource.onerror = (event) => {
      setError(new Error('EventSource failed'));
      setIsConnected(false);
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [url, enabled]);

  return { data, isConnected, error };
} 