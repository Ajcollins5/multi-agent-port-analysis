import axios from 'axios';
import { StockData, PortfolioSummary, Insight, APIResponse, AnalysisResult, Event, KnowledgeEvolution } from '@/types';

// Base API configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:3000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Enhanced API endpoints matching backend capabilities
export const portfolioAPI = {
  // Health check
  healthCheck: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.get('/api/app_supabase?action=health');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Health check failed'
      };
    }
  },

  // Get portfolio summary and analysis
  getPortfolioSummary: async (): Promise<APIResponse<PortfolioSummary>> => {
    try {
      const response = await api.post('/api/app_supabase', {
        action: 'get_portfolio_analysis'
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Portfolio analysis failed'
      };
    }
  },

  // Analyze individual ticker
  analyzeTicker: async (ticker: string): Promise<APIResponse<AnalysisResult>> => {
    try {
      const response = await api.post('/api/app_supabase', {
        action: 'analyze_ticker',
        ticker: ticker.toUpperCase()
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Ticker analysis failed'
      };
    }
  },

  // Get recent insights
  getInsights: async (filters?: {
    ticker?: string;
    agent?: string;
    impact_level?: string;
    time_window_hours?: number;
  }): Promise<APIResponse<{ insights: Insight[]; total_count: number }>> => {
    try {
      const response = await api.post('/api/app_supabase', {
        action: 'get_insights',
        ...filters
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch insights'
      };
    }
  },

  // Get events
  getEvents: async (filters?: {
    ticker?: string;
    event_type?: string;
    severity?: string;
    time_window_hours?: number;
  }): Promise<APIResponse<{ events: Event[]; total_count: number }>> => {
    try {
      const response = await api.post('/api/app_supabase', {
        action: 'get_events',
        ...filters
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch events'
      };
    }
  },

  // Get knowledge evolution
  getKnowledgeEvolution: async (filters?: {
    ticker?: string;
    evolution_type?: string;
    agent?: string;
    time_window_hours?: number;
  }): Promise<APIResponse<KnowledgeEvolution>> => {
    try {
      const response = await api.post('/api/app_supabase', {
        action: 'get_knowledge_evolution',
        ...filters
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch knowledge evolution'
      };
    }
  },

  // Get system status
  getSystemStatus: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/app_supabase', {
        action: 'get_system_status'
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to fetch system status'
      };
    }
  }
};

// Knowledge curator API
export const knowledgeAPI = {
  // Quality assessment
  qualityAssessment: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/agents/knowledge_curator', {
        action: 'quality_assessment'
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Quality assessment failed'
      };
    }
  },

  // Identify knowledge gaps
  identifyGaps: async (timeWindowHours: number = 24): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/agents/knowledge_curator', {
        action: 'identify_gaps',
        time_window_hours: timeWindowHours
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Gap identification failed'
      };
    }
  },

  // Get quality evolution
  getQualityEvolution: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/agents/knowledge_curator', {
        action: 'quality_evolution'
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Quality evolution failed'
      };
    }
  }
};

// Email notifications API
export const emailAPI = {
  // Send email
  sendEmail: async (to_email: string, subject: string, body: string): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/notifications/enhanced_email_service', {
        action: 'send_email',
        to_email,
        subject,
        html_content: body
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to send email'
      };
    }
  },

  // Send templated email
  sendTemplatedEmail: async (templateName: string, templateData: any, toEmail?: string): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/notifications/enhanced_email_service', {
        action: 'send_templated',
        template_name: templateName,
        template_data: templateData,
        to_email: toEmail
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to send templated email'
      };
    }
  },

  // Test email configuration
  testConfiguration: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/notifications/enhanced_email_service', {
        action: 'test_config'
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Email configuration test failed'
      };
    }
  },

  // Get email provider status
  getProviderStatus: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.get('/api/notifications/enhanced_email_service');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to get email provider status'
      };
    }
  }
};

// Scheduler API
export const schedulerAPI = {
  // Get scheduled jobs
  getJobs: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/scheduler/vercel_cron_jobs', {
        action: 'get_jobs'
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to get scheduled jobs'
      };
    }
  },

  // Get job history
  getJobHistory: async (limit: number = 20): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/scheduler/vercel_cron_jobs', {
        action: 'get_history',
        limit
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to get job history'
      };
    }
  },

  // Get service status
  getServiceStatus: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.get('/api/scheduler/vercel_cron_jobs');
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to get scheduler status'
      };
    }
  },

  // Create job
  createJob: async (jobConfig: any, service: string = 'external'): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/scheduler/vercel_cron_jobs', {
        action: 'create_job',
        job_config: jobConfig,
        service
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to create job'
      };
    }
  },

  // Delete job
  deleteJob: async (jobId: string): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/scheduler/vercel_cron_jobs', {
        action: 'delete_job',
        job_id: jobId
      });
      return {
        success: true,
        data: response.data
      };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.error || error.message || 'Failed to delete job'
      };
    }
  }
};

// Popular stocks for quick analysis
export const POPULAR_STOCKS = [
  { ticker: 'AAPL', name: 'Apple Inc.', sector: 'Technology' },
  { ticker: 'GOOGL', name: 'Alphabet Inc.', sector: 'Technology' },
  { ticker: 'MSFT', name: 'Microsoft Corporation', sector: 'Technology' },
  { ticker: 'AMZN', name: 'Amazon.com Inc.', sector: 'Consumer Discretionary' },
  { ticker: 'TSLA', name: 'Tesla Inc.', sector: 'Consumer Discretionary' },
  { ticker: 'META', name: 'Meta Platforms Inc.', sector: 'Communication Services' },
  { ticker: 'NVDA', name: 'NVIDIA Corporation', sector: 'Technology' },
  { ticker: 'NFLX', name: 'Netflix Inc.', sector: 'Communication Services' },
  { ticker: 'JPM', name: 'JPMorgan Chase & Co.', sector: 'Financial Services' },
  { ticker: 'V', name: 'Visa Inc.', sector: 'Financial Services' },
  { ticker: 'JNJ', name: 'Johnson & Johnson', sector: 'Healthcare' },
  { ticker: 'WMT', name: 'Walmart Inc.', sector: 'Consumer Staples' },
  { ticker: 'PG', name: 'Procter & Gamble Co.', sector: 'Consumer Staples' },
  { ticker: 'UNH', name: 'UnitedHealth Group Inc.', sector: 'Healthcare' },
  { ticker: 'HD', name: 'Home Depot Inc.', sector: 'Consumer Discretionary' },
  { ticker: 'MA', name: 'Mastercard Inc.', sector: 'Financial Services' },
  { ticker: 'BAC', name: 'Bank of America Corp.', sector: 'Financial Services' },
  { ticker: 'XOM', name: 'Exxon Mobil Corporation', sector: 'Energy' },
  { ticker: 'CVX', name: 'Chevron Corporation', sector: 'Energy' },
  { ticker: 'LLY', name: 'Eli Lilly and Company', sector: 'Healthcare' }
];

// Utility functions
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

export const formatPercentage = (value: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
};

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const formatShortDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
};

export const getRiskColor = (risk: string): string => {
  switch (risk?.toUpperCase()) {
    case 'HIGH':
      return 'text-red-600 bg-red-50 border-red-200';
    case 'MEDIUM':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'LOW':
      return 'text-green-600 bg-green-50 border-green-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

export const getImpactColor = (impact: string): string => {
  switch (impact?.toUpperCase()) {
    case 'HIGH':
      return 'text-red-700 bg-red-100 border-red-200';
    case 'MEDIUM':
      return 'text-yellow-700 bg-yellow-100 border-yellow-200';
    case 'LOW':
      return 'text-green-700 bg-green-100 border-green-200';
    default:
      return 'text-gray-700 bg-gray-100 border-gray-200';
  }
};

export const getStatusColor = (status: string): string => {
  switch (status?.toLowerCase()) {
    case 'healthy':
    case 'connected':
    case 'active':
      return 'text-green-600 bg-green-50 border-green-200';
    case 'degraded':
    case 'warning':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'error':
    case 'disconnected':
    case 'unhealthy':
      return 'text-red-600 bg-red-50 border-red-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
}; 