import axios from 'axios';
import { StockData, PortfolioSummary, Insight, APIResponse, AnalysisResult } from '@/types';

// Base API configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:3000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const portfolioAPI = {
  // Get portfolio summary and analysis
  getPortfolioSummary: async (): Promise<APIResponse<PortfolioSummary>> => {
    try {
      const response = await api.post('/api/app', {
        action: 'portfolio_analysis'
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
      const response = await api.post('/api/app', {
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
  getInsights: async (): Promise<APIResponse<{ insights: Insight[]; total_count: number }>> => {
    try {
      const response = await api.post('/api/app', {
        action: 'insights'
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

  // Send test email
  sendTestEmail: async (subject: string, message: string): Promise<APIResponse<any>> => {
    try {
      const response = await api.post('/api/app', {
        action: 'send_test_email',
        subject,
        message
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

  // Get system status
  getSystemStatus: async (): Promise<APIResponse<any>> => {
    try {
      const response = await api.get('/api/app');
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

export const getRiskColor = (risk: string): string => {
  switch (risk?.toUpperCase()) {
    case 'HIGH':
      return 'text-error-600 bg-error-50';
    case 'MEDIUM':
      return 'text-warning-600 bg-warning-50';
    case 'LOW':
      return 'text-success-600 bg-success-50';
    default:
      return 'text-gray-600 bg-gray-50';
  }
};

export const getImpactColor = (impact: string): string => {
  switch (impact?.toUpperCase()) {
    case 'HIGH':
      return 'text-error-700 bg-error-100 border-error-200';
    case 'MEDIUM':
      return 'text-warning-700 bg-warning-100 border-warning-200';
    case 'LOW':
      return 'text-success-700 bg-success-100 border-success-200';
    default:
      return 'text-gray-700 bg-gray-100 border-gray-200';
  }
}; 