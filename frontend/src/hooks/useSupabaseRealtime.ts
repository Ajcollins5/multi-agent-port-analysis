import { useState, useEffect, useCallback, useRef } from 'react';
import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { RealtimeChannel, RealtimePostgresChangesPayload } from '@supabase/supabase-js';

// Configuration
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

// Types
interface Insight {
  id: string;
  ticker: string;
  insight: string;
  agent: string;
  timestamp: string;
  volatility?: number;
  impact_level?: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence?: number;
  metadata?: Record<string, any>;
  refined: boolean;
  original_insight?: string;
  created_at: string;
  updated_at: string;
}

interface Event {
  id: string;
  event_type: string;
  ticker: string;
  message: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  timestamp: string;
  volatility?: number;
  volume_spike?: number;
  portfolio_risk?: 'LOW' | 'MEDIUM' | 'HIGH';
  correlation_data?: Record<string, any>;
  metadata?: Record<string, any>;
  created_at: string;
}

interface KnowledgeEvolution {
  id: string;
  ticker: string;
  evolution_type: string;
  previous_insight?: string;
  refined_insight: string;
  improvement_score: number;
  agent: string;
  timestamp: string;
  context?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

interface PortfolioAnalysis {
  id: string;
  portfolio_size: number;
  analyzed_stocks: number;
  high_impact_count: number;
  portfolio_risk: 'LOW' | 'MEDIUM' | 'HIGH';
  timestamp: string;
  analysis_duration: number;
  agents_used: string[];
  synthesis_summary?: string;
  metadata?: Record<string, any>;
  created_at: string;
}

interface SystemMetric {
  id: string;
  metric_type: string;
  metric_value: number;
  timestamp: string;
  additional_data?: Record<string, any>;
  created_at: string;
}

interface RealtimeState {
  insights: Insight[];
  events: Event[];
  knowledgeEvolution: KnowledgeEvolution[];
  portfolioAnalysis: PortfolioAnalysis[];
  systemMetrics: SystemMetric[];
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  lastUpdate: string | null;
}

interface UseSupabaseRealtimeOptions {
  enableInsights?: boolean;
  enableEvents?: boolean;
  enableKnowledgeEvolution?: boolean;
  enablePortfolioAnalysis?: boolean;
  enableSystemMetrics?: boolean;
  maxRecords?: number;
  tickerFilter?: string;
  agentFilter?: string;
  severityFilter?: string;
  onInsightReceived?: (insight: Insight) => void;
  onEventReceived?: (event: Event) => void;
  onKnowledgeEvolutionReceived?: (evolution: KnowledgeEvolution) => void;
  onPortfolioAnalysisReceived?: (analysis: PortfolioAnalysis) => void;
  onSystemMetricReceived?: (metric: SystemMetric) => void;
  onError?: (error: Error) => void;
}

export const useSupabaseRealtime = (options: UseSupabaseRealtimeOptions = {}) => {
  const {
    enableInsights = true,
    enableEvents = true,
    enableKnowledgeEvolution = true,
    enablePortfolioAnalysis = true,
    enableSystemMetrics = false,
    maxRecords = 100,
    tickerFilter,
    agentFilter,
    severityFilter,
    onInsightReceived,
    onEventReceived,
    onKnowledgeEvolutionReceived,
    onPortfolioAnalysisReceived,
    onSystemMetricReceived,
    onError
  } = options;

  const [state, setState] = useState<RealtimeState>({
    insights: [],
    events: [],
    knowledgeEvolution: [],
    portfolioAnalysis: [],
    systemMetrics: [],
    connectionStatus: 'connecting',
    lastUpdate: null
  });

  const supabaseRef = useRef<SupabaseClient | null>(null);
  const channelsRef = useRef<RealtimeChannel[]>([]);
  const mountedRef = useRef(true);

  // Initialize Supabase client
  useEffect(() => {
    try {
      supabaseRef.current = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
        realtime: {
          params: {
            eventsPerSecond: 10,
          },
        },
      });
      
      setState(prev => ({ ...prev, connectionStatus: 'connected' }));
    } catch (error) {
      console.error('Failed to initialize Supabase client:', error);
      setState(prev => ({ ...prev, connectionStatus: 'error' }));
      onError?.(error as Error);
    }
  }, [onError]);

  // Fetch initial data
  const fetchInitialData = useCallback(async () => {
    if (!supabaseRef.current || !mountedRef.current) return;

    try {
      const promises = [];

      // Fetch insights
      if (enableInsights) {
        let insightsQuery = supabaseRef.current
          .from('insights')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(maxRecords);

        if (tickerFilter) {
          insightsQuery = insightsQuery.eq('ticker', tickerFilter);
        }
        if (agentFilter) {
          insightsQuery = insightsQuery.eq('agent', agentFilter);
        }

        promises.push(insightsQuery);
      }

      // Fetch events
      if (enableEvents) {
        let eventsQuery = supabaseRef.current
          .from('events')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(maxRecords);

        if (tickerFilter) {
          eventsQuery = eventsQuery.eq('ticker', tickerFilter);
        }
        if (severityFilter) {
          eventsQuery = eventsQuery.eq('severity', severityFilter);
        }

        promises.push(eventsQuery);
      }

      // Fetch knowledge evolution
      if (enableKnowledgeEvolution) {
        let knowledgeQuery = supabaseRef.current
          .from('knowledge_evolution')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(maxRecords);

        if (tickerFilter) {
          knowledgeQuery = knowledgeQuery.eq('ticker', tickerFilter);
        }
        if (agentFilter) {
          knowledgeQuery = knowledgeQuery.eq('agent', agentFilter);
        }

        promises.push(knowledgeQuery);
      }

      // Fetch portfolio analysis
      if (enablePortfolioAnalysis) {
        const portfolioQuery = supabaseRef.current
          .from('portfolio_analysis')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(maxRecords);

        promises.push(portfolioQuery);
      }

      // Fetch system metrics
      if (enableSystemMetrics) {
        const metricsQuery = supabaseRef.current
          .from('system_metrics')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(maxRecords);

        promises.push(metricsQuery);
      }

      const results = await Promise.all(promises);
      let resultIndex = 0;

      const updates: Partial<RealtimeState> = {};

      if (enableInsights) {
        const { data: insights, error } = results[resultIndex++];
        if (error) throw error;
        updates.insights = insights || [];
      }

      if (enableEvents) {
        const { data: events, error } = results[resultIndex++];
        if (error) throw error;
        updates.events = events || [];
      }

      if (enableKnowledgeEvolution) {
        const { data: knowledge, error } = results[resultIndex++];
        if (error) throw error;
        updates.knowledgeEvolution = knowledge || [];
      }

      if (enablePortfolioAnalysis) {
        const { data: portfolio, error } = results[resultIndex++];
        if (error) throw error;
        updates.portfolioAnalysis = portfolio || [];
      }

      if (enableSystemMetrics) {
        const { data: metrics, error } = results[resultIndex++];
        if (error) throw error;
        updates.systemMetrics = metrics || [];
      }

      if (mountedRef.current) {
        setState(prev => ({
          ...prev,
          ...updates,
          lastUpdate: new Date().toISOString()
        }));
      }

    } catch (error) {
      console.error('Failed to fetch initial data:', error);
      onError?.(error as Error);
    }
  }, [enableInsights, enableEvents, enableKnowledgeEvolution, enablePortfolioAnalysis, enableSystemMetrics, maxRecords, tickerFilter, agentFilter, severityFilter, onError]);

  // Setup real-time subscriptions
  useEffect(() => {
    if (!supabaseRef.current || !mountedRef.current) return;

    const setupSubscriptions = () => {
      // Clear existing channels
      channelsRef.current.forEach(channel => {
        supabaseRef.current?.removeChannel(channel);
      });
      channelsRef.current = [];

      // Insights subscription
      if (enableInsights) {
        const insightsChannel = supabaseRef.current.channel('insights_changes')
          .on('postgres_changes', {
            event: '*',
            schema: 'public',
            table: 'insights',
            filter: tickerFilter ? `ticker=eq.${tickerFilter}` : undefined
          }, (payload: RealtimePostgresChangesPayload<Insight>) => {
            if (!mountedRef.current) return;

            const { eventType, new: newRecord, old: oldRecord } = payload;

            setState(prev => {
              let newInsights = [...prev.insights];

              switch (eventType) {
                case 'INSERT':
                  if (newRecord) {
                    newInsights = [newRecord, ...newInsights.slice(0, maxRecords - 1)];
                    onInsightReceived?.(newRecord);
                  }
                  break;
                case 'UPDATE':
                  if (newRecord) {
                    newInsights = newInsights.map(insight => 
                      insight.id === newRecord.id ? newRecord : insight
                    );
                    onInsightReceived?.(newRecord);
                  }
                  break;
                case 'DELETE':
                  if (oldRecord) {
                    newInsights = newInsights.filter(insight => insight.id !== oldRecord.id);
                  }
                  break;
              }

              return {
                ...prev,
                insights: newInsights,
                lastUpdate: new Date().toISOString()
              };
            });
          })
          .subscribe();

        channelsRef.current.push(insightsChannel);
      }

      // Events subscription
      if (enableEvents) {
        const eventsChannel = supabaseRef.current.channel('events_changes')
          .on('postgres_changes', {
            event: '*',
            schema: 'public',
            table: 'events',
            filter: tickerFilter ? `ticker=eq.${tickerFilter}` : undefined
          }, (payload: RealtimePostgresChangesPayload<Event>) => {
            if (!mountedRef.current) return;

            const { eventType, new: newRecord, old: oldRecord } = payload;

            setState(prev => {
              let newEvents = [...prev.events];

              switch (eventType) {
                case 'INSERT':
                  if (newRecord) {
                    newEvents = [newRecord, ...newEvents.slice(0, maxRecords - 1)];
                    onEventReceived?.(newRecord);
                  }
                  break;
                case 'UPDATE':
                  if (newRecord) {
                    newEvents = newEvents.map(event => 
                      event.id === newRecord.id ? newRecord : event
                    );
                    onEventReceived?.(newRecord);
                  }
                  break;
                case 'DELETE':
                  if (oldRecord) {
                    newEvents = newEvents.filter(event => event.id !== oldRecord.id);
                  }
                  break;
              }

              return {
                ...prev,
                events: newEvents,
                lastUpdate: new Date().toISOString()
              };
            });
          })
          .subscribe();

        channelsRef.current.push(eventsChannel);
      }

      // Knowledge evolution subscription
      if (enableKnowledgeEvolution) {
        const knowledgeChannel = supabaseRef.current.channel('knowledge_changes')
          .on('postgres_changes', {
            event: '*',
            schema: 'public',
            table: 'knowledge_evolution',
            filter: tickerFilter ? `ticker=eq.${tickerFilter}` : undefined
          }, (payload: RealtimePostgresChangesPayload<KnowledgeEvolution>) => {
            if (!mountedRef.current) return;

            const { eventType, new: newRecord, old: oldRecord } = payload;

            setState(prev => {
              let newKnowledge = [...prev.knowledgeEvolution];

              switch (eventType) {
                case 'INSERT':
                  if (newRecord) {
                    newKnowledge = [newRecord, ...newKnowledge.slice(0, maxRecords - 1)];
                    onKnowledgeEvolutionReceived?.(newRecord);
                  }
                  break;
                case 'UPDATE':
                  if (newRecord) {
                    newKnowledge = newKnowledge.map(knowledge => 
                      knowledge.id === newRecord.id ? newRecord : knowledge
                    );
                    onKnowledgeEvolutionReceived?.(newRecord);
                  }
                  break;
                case 'DELETE':
                  if (oldRecord) {
                    newKnowledge = newKnowledge.filter(knowledge => knowledge.id !== oldRecord.id);
                  }
                  break;
              }

              return {
                ...prev,
                knowledgeEvolution: newKnowledge,
                lastUpdate: new Date().toISOString()
              };
            });
          })
          .subscribe();

        channelsRef.current.push(knowledgeChannel);
      }

      // Portfolio analysis subscription
      if (enablePortfolioAnalysis) {
        const portfolioChannel = supabaseRef.current.channel('portfolio_changes')
          .on('postgres_changes', {
            event: '*',
            schema: 'public',
            table: 'portfolio_analysis'
          }, (payload: RealtimePostgresChangesPayload<PortfolioAnalysis>) => {
            if (!mountedRef.current) return;

            const { eventType, new: newRecord, old: oldRecord } = payload;

            setState(prev => {
              let newPortfolio = [...prev.portfolioAnalysis];

              switch (eventType) {
                case 'INSERT':
                  if (newRecord) {
                    newPortfolio = [newRecord, ...newPortfolio.slice(0, maxRecords - 1)];
                    onPortfolioAnalysisReceived?.(newRecord);
                  }
                  break;
                case 'UPDATE':
                  if (newRecord) {
                    newPortfolio = newPortfolio.map(analysis => 
                      analysis.id === newRecord.id ? newRecord : analysis
                    );
                    onPortfolioAnalysisReceived?.(newRecord);
                  }
                  break;
                case 'DELETE':
                  if (oldRecord) {
                    newPortfolio = newPortfolio.filter(analysis => analysis.id !== oldRecord.id);
                  }
                  break;
              }

              return {
                ...prev,
                portfolioAnalysis: newPortfolio,
                lastUpdate: new Date().toISOString()
              };
            });
          })
          .subscribe();

        channelsRef.current.push(portfolioChannel);
      }

      // System metrics subscription
      if (enableSystemMetrics) {
        const metricsChannel = supabaseRef.current.channel('metrics_changes')
          .on('postgres_changes', {
            event: '*',
            schema: 'public',
            table: 'system_metrics'
          }, (payload: RealtimePostgresChangesPayload<SystemMetric>) => {
            if (!mountedRef.current) return;

            const { eventType, new: newRecord, old: oldRecord } = payload;

            setState(prev => {
              let newMetrics = [...prev.systemMetrics];

              switch (eventType) {
                case 'INSERT':
                  if (newRecord) {
                    newMetrics = [newRecord, ...newMetrics.slice(0, maxRecords - 1)];
                    onSystemMetricReceived?.(newRecord);
                  }
                  break;
                case 'UPDATE':
                  if (newRecord) {
                    newMetrics = newMetrics.map(metric => 
                      metric.id === newRecord.id ? newRecord : metric
                    );
                    onSystemMetricReceived?.(newRecord);
                  }
                  break;
                case 'DELETE':
                  if (oldRecord) {
                    newMetrics = newMetrics.filter(metric => metric.id !== oldRecord.id);
                  }
                  break;
              }

              return {
                ...prev,
                systemMetrics: newMetrics,
                lastUpdate: new Date().toISOString()
              };
            });
          })
          .subscribe();

        channelsRef.current.push(metricsChannel);
      }
    };

    setupSubscriptions();
    fetchInitialData();

    return () => {
      channelsRef.current.forEach(channel => {
        supabaseRef.current?.removeChannel(channel);
      });
      channelsRef.current = [];
    };
  }, [enableInsights, enableEvents, enableKnowledgeEvolution, enablePortfolioAnalysis, enableSystemMetrics, maxRecords, tickerFilter, agentFilter, severityFilter, fetchInitialData]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
  }, []);

  // Utility functions
  const getInsightsByTicker = useCallback((ticker: string) => {
    return state.insights.filter(insight => insight.ticker === ticker);
  }, [state.insights]);

  const getEventsByTicker = useCallback((ticker: string) => {
    return state.events.filter(event => event.ticker === ticker);
  }, [state.events]);

  const getEventsBySeverity = useCallback((severity: string) => {
    return state.events.filter(event => event.severity === severity);
  }, [state.events]);

  const getLatestPortfolioAnalysis = useCallback(() => {
    return state.portfolioAnalysis[0] || null;
  }, [state.portfolioAnalysis]);

  const getKnowledgeEvolutionByTicker = useCallback((ticker: string) => {
    return state.knowledgeEvolution.filter(evolution => evolution.ticker === ticker);
  }, [state.knowledgeEvolution]);

  const refreshData = useCallback(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  return {
    ...state,
    // Utility functions
    getInsightsByTicker,
    getEventsByTicker,
    getEventsBySeverity,
    getLatestPortfolioAnalysis,
    getKnowledgeEvolutionByTicker,
    refreshData,
    // Connection info
    isConnected: state.connectionStatus === 'connected',
    isConnecting: state.connectionStatus === 'connecting',
    hasError: state.connectionStatus === 'error',
  };
};

export default useSupabaseRealtime;

// Export types for use in components
export type {
  Insight,
  Event,
  KnowledgeEvolution,
  PortfolioAnalysis,
  SystemMetric,
  RealtimeState,
  UseSupabaseRealtimeOptions
}; 