// Stock and portfolio types
export interface StockData {
  ticker: string;
  current_price: number;
  volatility: number;
  impact_level: 'HIGH' | 'MEDIUM' | 'LOW';
  high_impact: boolean;
  timestamp: string;
  price_change?: number;
  volume?: number;
  market_cap?: number;
}

export interface PortfolioSummary {
  portfolio_size: number;
  analyzed_stocks: number;
  high_impact_count: number;
  portfolio_risk: 'HIGH' | 'MEDIUM' | 'LOW';
  timestamp: string;
  results: StockData[];
}

export interface Insight {
  ticker: string;
  insight: string;
  timestamp: string;
  id?: string;
}

export interface Event {
  id: string;
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';
  ticker: string;
  message: string;
  timestamp: string;
}

export interface KnowledgeEvolution {
  ticker: string;
  evolution_info: string;
  historical_insights: string[];
  timeline: {
    date: string;
    insights: string[];
  }[];
}

export interface SchedulerConfig {
  isRunning: boolean;
  interval: number; // in seconds
  lastRun?: string;
  nextRun?: string;
}

export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface AnalysisResult {
  ticker: string;
  current_price: number;
  volatility: number;
  impact_level: string;
  high_impact: boolean;
  email_sent?: boolean;
  insights?: Insight[];
}

export interface PopularStock {
  ticker: string;
  name: string;
  sector: string;
}

export interface MetricCard {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: string;
} 