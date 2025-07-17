import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { portfolioAPI } from '@/utils/api';
import { PortfolioSummary, Insight, AnalysisResult, Event } from '@/types';

// Portfolio data hook
export const usePortfolioData = () => {
  return useQuery(
    'portfolio-summary',
    portfolioAPI.getPortfolioSummary,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
      retry: 3,
      staleTime: 10000, // Data is fresh for 10 seconds
    }
  );
};

// Insights data hook
export const useInsights = () => {
  return useQuery(
    'insights',
    portfolioAPI.getInsights,
    {
      refetchInterval: 60000, // Refetch every minute
      retry: 2,
      staleTime: 30000, // Data is fresh for 30 seconds
    }
  );
};

// System status hook
export const useSystemStatus = () => {
  return useQuery(
    'system-status',
    portfolioAPI.getSystemStatus,
    {
      refetchInterval: 120000, // Refetch every 2 minutes
      retry: 2,
      staleTime: 60000, // Data is fresh for 1 minute
    }
  );
};

// Ticker analysis mutation
export const useAnalyzeTicker = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    (ticker: string) => portfolioAPI.analyzeTicker(ticker),
    {
      onSuccess: () => {
        // Invalidate and refetch portfolio and insights data
        queryClient.invalidateQueries('portfolio-summary');
        queryClient.invalidateQueries('insights');
      },
    }
  );
};

// Email notification mutation
export const useSendEmail = () => {
  return useMutation(
    ({ subject, message }: { subject: string; message: string }) => 
      portfolioAPI.sendTestEmail(subject, message)
  );
};

// Real-time events hook with local state management
export const useEvents = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [isAutoRefresh, setIsAutoRefresh] = useState(false);

  const addEvent = useCallback((event: Omit<Event, 'id'>) => {
    const newEvent: Event = {
      ...event,
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
    };
    setEvents(prev => [newEvent, ...prev].slice(0, 100)); // Keep last 100 events
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  const toggleAutoRefresh = useCallback(() => {
    setIsAutoRefresh(prev => !prev);
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    if (!isAutoRefresh) return;

    const interval = setInterval(() => {
      // Add a system event to simulate real-time updates
      addEvent({
        type: 'INFO',
        ticker: 'SYSTEM',
        message: 'Auto-refresh check completed',
      });
    }, 5000);

    return () => clearInterval(interval);
  }, [isAutoRefresh, addEvent]);

  return {
    events,
    isAutoRefresh,
    addEvent,
    clearEvents,
    toggleAutoRefresh,
  };
};

// Scheduler hook with local state management
export const useScheduler = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [interval, setInterval] = useState(3600); // 1 hour in seconds
  const [lastRun, setLastRun] = useState<string | null>(null);
  const [nextRun, setNextRun] = useState<string | null>(null);

  const startScheduler = useCallback(() => {
    setIsRunning(true);
    setLastRun(new Date().toISOString());
    
    // Calculate next run time
    const nextRunTime = new Date(Date.now() + interval * 1000);
    setNextRun(nextRunTime.toISOString());
  }, [interval]);

  const stopScheduler = useCallback(() => {
    setIsRunning(false);
    setNextRun(null);
  }, []);

  const updateInterval = useCallback((newInterval: number) => {
    setInterval(newInterval);
    
    // If scheduler is running, update next run time
    if (isRunning) {
      const nextRunTime = new Date(Date.now() + newInterval * 1000);
      setNextRun(nextRunTime.toISOString());
    }
  }, [isRunning]);

  return {
    isRunning,
    interval,
    lastRun,
    nextRun,
    startScheduler,
    stopScheduler,
    updateInterval,
  };
};

// Knowledge evolution hook (mock data for now)
export const useKnowledgeEvolution = (ticker?: string) => {
  const [evolutionData, setEvolutionData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchEvolution = useCallback(async (selectedTicker: string) => {
    setIsLoading(true);
    
    // Mock data - in real implementation, this would call an API
    setTimeout(() => {
      setEvolutionData({
        ticker: selectedTicker,
        evolution_info: `Knowledge evolution for ${selectedTicker} shows increasing sophistication in risk assessment and market correlation analysis over the past 30 days.`,
        historical_insights: [
          `${selectedTicker} volatility analysis refined based on recent market patterns`,
          `Enhanced risk assessment for ${selectedTicker} following earnings announcement`,
          `Updated correlation analysis with market indices for ${selectedTicker}`,
          `Improved sentiment analysis accuracy for ${selectedTicker} news events`,
        ],
        timeline: [
          {
            date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            insights: [`Initial analysis framework established for ${selectedTicker}`]
          },
          {
            date: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            insights: [`Risk model improvements for ${selectedTicker}`]
          },
          {
            date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
            insights: [`Market correlation analysis enhanced for ${selectedTicker}`]
          },
          {
            date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(),
            insights: [`Latest insights incorporated for ${selectedTicker}`]
          }
        ]
      });
      setIsLoading(false);
    }, 1000);
  }, []);

  useEffect(() => {
    if (ticker) {
      fetchEvolution(ticker);
    }
  }, [ticker, fetchEvolution]);

  return {
    evolutionData,
    isLoading,
    fetchEvolution,
  };
}; 