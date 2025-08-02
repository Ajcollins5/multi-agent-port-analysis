import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  portfolioAPI, 
  knowledgeAPI, 
  emailAPI, 
  schedulerAPI 
} from '@/utils/api';
import { 
  PortfolioSummary, 
  Insight, 
  AnalysisResult, 
  Event, 
  KnowledgeEvolution,
  KnowledgeQuality,
  SystemStatus,
  SchedulerJob,
  JobHistory,
  EmailStatus,
  FilterOptions,
  RealTimeUpdate,
  DashboardMetrics
} from '@/types';

// Health check hook
export const useHealthCheck = () => {
  return useQuery(
    'health-check',
    portfolioAPI.healthCheck,
    {
      refetchInterval: 60000, // Check every minute
      retry: 3,
      staleTime: 30000,
    }
  );
};

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

// Enhanced insights hook with filters
export const useInsights = (filters?: FilterOptions) => {
  return useQuery(
    ['insights', filters],
    () => portfolioAPI.getInsights(filters),
    {
      refetchInterval: 60000, // Refetch every minute
      retry: 2,
      staleTime: 30000, // Data is fresh for 30 seconds
    }
  );
};

// Events hook with filters
export const useEvents = (filters?: FilterOptions) => {
  return useQuery(
    ['events', filters],
    () => portfolioAPI.getEvents(filters),
    {
      refetchInterval: 45000, // Refetch every 45 seconds
      retry: 2,
      staleTime: 20000,
    }
  );
};

// Knowledge evolution hook
export const useKnowledgeEvolution = (filters?: FilterOptions) => {
  return useQuery(
    ['knowledge-evolution', filters],
    () => portfolioAPI.getKnowledgeEvolution(filters),
    {
      refetchInterval: 120000, // Refetch every 2 minutes
      retry: 2,
      staleTime: 60000,
    }
  );
};

// System status hook
export const useSystemStatus = () => {
  return useQuery(
    'system-status',
    portfolioAPI.getSystemStatus,
    {
      refetchInterval: 90000, // Refetch every 90 seconds
      retry: 2,
      staleTime: 45000,
    }
  );
};

// Knowledge quality assessment hook
export const useKnowledgeQuality = () => {
  return useQuery(
    'knowledge-quality',
    knowledgeAPI.qualityAssessment,
    {
      refetchInterval: 300000, // Refetch every 5 minutes
      retry: 2,
      staleTime: 120000,
    }
  );
};

// Knowledge gaps hook
export const useKnowledgeGaps = (timeWindowHours: number = 24) => {
  return useQuery(
    ['knowledge-gaps', timeWindowHours],
    () => knowledgeAPI.identifyGaps(timeWindowHours),
    {
      refetchInterval: 300000, // Refetch every 5 minutes
      retry: 2,
      staleTime: 120000,
    }
  );
};

// Quality evolution hook
export const useQualityEvolution = () => {
  return useQuery(
    'quality-evolution',
    knowledgeAPI.getQualityEvolution,
    {
      refetchInterval: 600000, // Refetch every 10 minutes
      retry: 2,
      staleTime: 300000,
    }
  );
};

// Email status hook
export const useEmailStatus = () => {
  return useQuery(
    'email-status',
    emailAPI.getProviderStatus,
    {
      refetchInterval: 180000, // Refetch every 3 minutes
      retry: 2,
      staleTime: 90000,
    }
  );
};

// Scheduler jobs hook
export const useSchedulerJobs = () => {
  return useQuery(
    'scheduler-jobs',
    schedulerAPI.getJobs,
    {
      refetchInterval: 120000, // Refetch every 2 minutes
      retry: 2,
      staleTime: 60000,
    }
  );
};

// Job history hook
export const useJobHistory = (limit: number = 20) => {
  return useQuery(
    ['job-history', limit],
    () => schedulerAPI.getJobHistory(limit),
    {
      refetchInterval: 180000, // Refetch every 3 minutes
      retry: 2,
      staleTime: 90000,
    }
  );
};

// Scheduler service status hook
export const useSchedulerStatus = () => {
  return useQuery(
    'scheduler-status',
    schedulerAPI.getServiceStatus,
    {
      refetchInterval: 300000, // Refetch every 5 minutes
      retry: 2,
      staleTime: 180000,
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
        // Invalidate and refetch related data
        queryClient.invalidateQueries('portfolio-summary');
        queryClient.invalidateQueries('insights');
        queryClient.invalidateQueries('events');
        queryClient.invalidateQueries('knowledge-evolution');
      },
    }
  );
};

// Email sending mutations
export const useSendEmail = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ to_email, subject, body }: { to_email: string; subject: string; body: string }) => 
      emailAPI.sendEmail(to_email, subject, body),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('email-status');
      },
    }
  );
};

export const useSendTemplatedEmail = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ templateName, templateData, toEmail }: { templateName: string; templateData: any; toEmail?: string }) => 
      emailAPI.sendTemplatedEmail(templateName, templateData, toEmail),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('email-status');
      },
    }
  );
};

export const useTestEmailConfiguration = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    emailAPI.testConfiguration,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('email-status');
      },
    }
  );
};

// Scheduler mutations
export const useCreateJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    ({ jobConfig, service }: { jobConfig: any; service?: string }) => 
      schedulerAPI.createJob(jobConfig, service),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('scheduler-jobs');
        queryClient.invalidateQueries('scheduler-status');
      },
    }
  );
};

export const useDeleteJob = () => {
  const queryClient = useQueryClient();
  
  return useMutation(
    (jobId: string) => schedulerAPI.deleteJob(jobId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('scheduler-jobs');
        queryClient.invalidateQueries('job-history');
      },
    }
  );
};

// Real-time updates hook
export const useRealTimeUpdates = () => {
  const [updates, setUpdates] = useState<RealTimeUpdate[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const queryClient = useQueryClient();

  const addUpdate = useCallback((update: RealTimeUpdate) => {
    setUpdates(prev => [update, ...prev].slice(0, 100)); // Keep last 100 updates
    
    // Invalidate related queries based on update type
    switch (update.type) {
      case 'insight':
        queryClient.invalidateQueries('insights');
        break;
      case 'event':
        queryClient.invalidateQueries('events');
        break;
      case 'portfolio':
        queryClient.invalidateQueries('portfolio-summary');
        break;
      case 'system':
        queryClient.invalidateQueries('system-status');
        break;
      case 'job':
        queryClient.invalidateQueries('scheduler-jobs');
        break;
    }
  }, [queryClient]);

  const clearUpdates = useCallback(() => {
    setUpdates([]);
  }, []);

  // Simulated real-time updates (in production, use WebSocket or Server-Sent Events)
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate periodic updates
      const now = new Date().toISOString();
      const randomUpdate: RealTimeUpdate = {
        type: 'system',
        data: { message: 'System heartbeat check' },
        timestamp: now,
        priority: 'low'
      };
      
      addUpdate(randomUpdate);
      setIsConnected(true);
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [addUpdate]);

  return {
    updates,
    isConnected,
    addUpdate,
    clearUpdates,
  };
};

// Dashboard metrics hook
export const useDashboardMetrics = () => {
  const { data: portfolioData } = usePortfolioData();
  const { data: insightsData } = useInsights();
  const { data: eventsData } = useEvents();
  const { data: systemStatus } = useSystemStatus();
  const { data: schedulerJobs } = useSchedulerJobs();
  const { data: emailStatus } = useEmailStatus();

  const metrics: DashboardMetrics = {
    total_insights: insightsData?.data?.total_count || 0,
    total_events: eventsData?.data?.total_count || 0,
    portfolio_value: portfolioData?.data?.total_value || 0,
    risk_score: portfolioData?.data?.risk_score || 0,
    active_jobs: schedulerJobs?.data?.active_jobs || 0,
    system_health: systemStatus?.data?.status === 'healthy' ? 100 : 
                   systemStatus?.data?.status === 'degraded' ? 50 : 0,
    recent_analysis: portfolioData?.data?.analyzed_stocks || 0,
    email_success_rate: emailStatus?.data?.success_rate || 0,
  };

  return metrics;
};

// Enhanced scheduler hook with state management
export const useScheduler = () => {
  const { data: jobs, isLoading: jobsLoading } = useSchedulerJobs();
  const { data: history, isLoading: historyLoading } = useJobHistory();
  const { data: status, isLoading: statusLoading } = useSchedulerStatus();
  const createJobMutation = useCreateJob();
  const deleteJobMutation = useDeleteJob();

  const activeJobs = jobs?.data?.scheduled_jobs?.filter((job: SchedulerJob) => job.status === 'active') || [];
  const completedJobs = jobs?.data?.scheduled_jobs?.filter((job: SchedulerJob) => job.status === 'completed') || [];
  const failedJobs = jobs?.data?.scheduled_jobs?.filter((job: SchedulerJob) => job.status === 'failed') || [];

  const createJob = useCallback((jobConfig: any, service?: string) => {
    return createJobMutation.mutateAsync({ jobConfig, service });
  }, [createJobMutation]);

  const deleteJob = useCallback((jobId: string) => {
    return deleteJobMutation.mutateAsync(jobId);
  }, [deleteJobMutation]);

  return {
    jobs: jobs?.data?.scheduled_jobs || [],
    history: history?.data?.job_history || [],
    status: status?.data,
    activeJobs,
    completedJobs,
    failedJobs,
    isLoading: jobsLoading || historyLoading || statusLoading,
    createJob,
    deleteJob,
    isCreating: createJobMutation.isLoading,
    isDeleting: deleteJobMutation.isLoading,
  };
};

// Advanced filtering hook
export const useAdvancedFilters = () => {
  const [filters, setFilters] = useState<FilterOptions>({
    time_window_hours: 24,
  });

  const updateFilter = useCallback((key: keyof FilterOptions, value: any) => {
    setFilters(prev => ({
      ...prev,
      [key]: value,
    }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters({
      time_window_hours: 24,
    });
  }, []);

  const clearFilter = useCallback((key: keyof FilterOptions) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      delete newFilters[key];
      return newFilters;
    });
  }, []);

  return {
    filters,
    updateFilter,
    resetFilters,
    clearFilter,
  };
}; 