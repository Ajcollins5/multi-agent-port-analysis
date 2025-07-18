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
  confidence?: number;
  agent?: string;
}

export interface PortfolioSummary {
  portfolio_size: number;
  analyzed_stocks: number;
  high_impact_count: number;
  portfolio_risk: 'HIGH' | 'MEDIUM' | 'LOW';
  timestamp: string;
  results: StockData[];
  total_value?: number;
  daily_change?: number;
  risk_score?: number;
}

export interface Insight {
  id?: string;
  ticker: string;
  insight: string;
  agent: string;
  timestamp: string;
  impact_level?: 'HIGH' | 'MEDIUM' | 'LOW';
  confidence?: number;
  volatility?: number;
  metadata?: any;
}

export interface Event {
  id: string;
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'CRITICAL';
  ticker: string;
  message: string;
  timestamp: string;
  severity?: 'HIGH' | 'MEDIUM' | 'LOW';
  event_type?: string;
  agent?: string;
  metadata?: any;
}

export interface KnowledgeEvolution {
  ticker: string;
  evolution_type: string;
  agent: string;
  evolution_info: string;
  historical_insights: string[];
  timeline: {
    date: string;
    insights: string[];
    quality_score?: number;
  }[];
  current_quality?: number;
  improvement_trend?: 'improving' | 'stable' | 'declining';
}

export interface KnowledgeGap {
  type: string;
  description: string;
  severity: 'HIGH' | 'MEDIUM' | 'LOW';
  agent?: string;
  recommendations?: string[];
  impact?: string;
}

export interface KnowledgeQuality {
  overall_score: number;
  quality_metrics: {
    completeness: number;
    accuracy: number;
    timeliness: number;
    relevance: number;
  };
  gaps: KnowledgeGap[];
  improvement_suggestions: string[];
  timestamp: string;
}

export interface SystemStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  services: {
    supabase_manager: boolean;
    supabase_risk_agent: boolean;
    supervisor: boolean;
    email_service?: boolean;
    scheduler?: boolean;
  };
  environment: {
    required_vars_present: boolean;
    missing_vars: string[];
  };
  database: string;
  performance_metrics?: {
    response_time: number;
    memory_usage: number;
    cpu_usage: number;
  };
}

export interface SchedulerJob {
  id: string;
  name: string;
  job_type: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  schedule: string;
  last_run?: string;
  next_run?: string;
  created_at: string;
  config: any;
  execution_count?: number;
  success_rate?: number;
}

export interface JobHistory {
  id: string;
  job_id: string;
  execution_time: string;
  duration: number;
  status: 'completed' | 'failed' | 'running';
  result?: any;
  error?: string;
}

export interface EmailProvider {
  name: string;
  status: 'available' | 'configured' | 'unavailable';
  priority: number;
  last_test?: string;
  success_rate?: number;
}

export interface EmailStatus {
  providers: EmailProvider[];
  default_provider: string;
  total_sent: number;
  success_rate: number;
  last_sent?: string;
}

export interface SchedulerConfig {
  isRunning: boolean;
  interval: number; // in seconds
  lastRun?: string;
  nextRun?: string;
  jobs: SchedulerJob[];
  service_status: any;
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
  confidence?: number;
  risk_score?: number;
  email_sent?: boolean;
  insights?: Insight[];
  events?: Event[];
  timestamp: string;
  agent_results?: {
    risk?: any;
    news?: any;
    events?: any;
    knowledge?: any;
  };
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
  trend?: number[];
  subtitle?: string;
}

export interface DashboardMetrics {
  total_insights: number;
  total_events: number;
  portfolio_value: number;
  risk_score: number;
  active_jobs: number;
  system_health: number;
  recent_analysis: number;
  email_success_rate: number;
}

export interface RealTimeUpdate {
  type: 'insight' | 'event' | 'portfolio' | 'system' | 'job';
  data: any;
  timestamp: string;
  priority: 'high' | 'medium' | 'low';
}

export interface FilterOptions {
  ticker?: string;
  agent?: string;
  impact_level?: 'HIGH' | 'MEDIUM' | 'LOW';
  event_type?: string;
  severity?: 'HIGH' | 'MEDIUM' | 'LOW';
  time_window_hours?: number;
  evolution_type?: string;
} 