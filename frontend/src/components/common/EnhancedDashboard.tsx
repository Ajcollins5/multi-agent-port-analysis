import React, { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { MetricCard } from '@/components/common/MetricCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { SystemStatusCard } from '@/components/common/SystemStatusCard';
import { EventsCard } from '@/components/common/EventsCard';
import { 
  usePortfolioData, 
  useInsights, 
  useEvents,
  useSystemStatus,
  useKnowledgeEvolution,
  useScheduler,
  useEmailStatus,
  useDashboardMetrics,
  useRealTimeUpdates,
  useAdvancedFilters,
  useAnalyzeTicker
} from '@/hooks/useApi';
import { formatCurrency, formatDate, getRiskColor, getImpactColor } from '@/utils/api';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  AlertTriangle,
  DollarSign,
  BarChart3,
  RefreshCw,
  Brain,
  Calendar,
  Mail,
  Server,
  Eye,
  Zap,
  Target,
  Globe,
  Users
} from 'lucide-react';

const EnhancedDashboard: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  // Advanced filters
  const { filters, updateFilter, resetFilters } = useAdvancedFilters();

  // Core data hooks
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError, refetch: refetchPortfolio } = usePortfolioData();
  const { data: insightsData, isLoading: insightsLoading, error: insightsError, refetch: refetchInsights } = useInsights(filters);
  const { data: eventsData, isLoading: eventsLoading, error: eventsError, refetch: refetchEvents } = useEvents(filters);
  const { data: systemStatus, isLoading: systemStatusLoading, error: systemStatusError } = useSystemStatus();
  const { data: knowledgeEvolution, isLoading: knowledgeLoading } = useKnowledgeEvolution(filters);
  const { data: emailStatus, isLoading: emailLoading } = useEmailStatus();
  
  // Scheduler data
  const { 
    activeJobs, 
    completedJobs, 
    failedJobs, 
    isLoading: schedulerLoading 
  } = useScheduler();

  // Real-time updates
  const { updates, isConnected, clearUpdates } = useRealTimeUpdates();

  // Dashboard metrics
  const dashboardMetrics = useDashboardMetrics();

  // Mutations
  const analyzeTicker = useAnalyzeTicker();

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([
      refetchPortfolio(),
      refetchInsights(),
      refetchEvents()
    ]);
    setRefreshing(false);
  };

  const handleTickerAnalysis = async (ticker: string) => {
    if (!ticker) return;
    try {
      await analyzeTicker.mutateAsync(ticker);
    } catch (error) {
      console.error('Analysis failed:', error);
    }
  };

  const portfolio = portfolioData?.data;
  const insights = insightsData?.data;
  const events = eventsData?.data;

  const isLoading = portfolioLoading || insightsLoading || eventsLoading || systemStatusLoading;
  const hasError = portfolioError || insightsError || eventsError || systemStatusError;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Enhanced Portfolio Dashboard</h1>
            <p className="text-gray-600">
              Real-time multi-agent portfolio analysis with advanced insights
            </p>
          </div>
          <div className="flex items-center space-x-4">
            {/* Real-time Status */}
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span className="text-sm text-gray-600">
                {isConnected ? 'Live' : 'Offline'}
              </span>
            </div>
            
            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>

        {/* Real-time Updates Ticker */}
        {updates.length > 0 && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Zap className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">
                  Latest Update: {updates[0].data.message || 'System update'}
                </span>
                <span className="text-xs text-blue-600">
                  {formatDate(updates[0].timestamp)}
                </span>
              </div>
              <button
                onClick={clearUpdates}
                className="text-blue-600 hover:text-blue-800 text-sm"
              >
                Clear ({updates.length})
              </button>
            </div>
          </div>
        )}

        {/* Enhanced Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Portfolio Value"
            value={formatCurrency(dashboardMetrics.portfolio_value)}
            change={portfolio?.daily_change}
            changeType={portfolio?.daily_change && portfolio.daily_change > 0 ? 'positive' : 'negative'}
            icon={DollarSign}
            trend={[65, 59, 80, 81, 56, 55, 40]}
          />
          
          <MetricCard
            title="Risk Score"
            value={dashboardMetrics.risk_score}
            subtitle={`${dashboardMetrics.recent_analysis} stocks analyzed`}
            icon={BarChart3}
            trend={[28, 48, 40, 19, 86, 27, 90]}
          />
          
          <MetricCard
            title="Active Insights"
            value={dashboardMetrics.total_insights}
            subtitle="AI-powered analysis"
            icon={Brain}
            trend={[0, 2, 5, 8, 12, 18, 25]}
          />
          
          <MetricCard
            title="System Health"
            value={`${dashboardMetrics.system_health}%`}
            subtitle={`${dashboardMetrics.active_jobs} active jobs`}
            icon={Activity}
            trend={[100, 95, 98, 92, 85, 90, 100]}
          />
        </div>

        {/* Additional Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Events"
            value={dashboardMetrics.total_events}
            subtitle="Real-time monitoring"
            icon={Eye}
            trend={[5, 8, 12, 15, 18, 22, 25]}
          />
          
          <MetricCard
            title="Email Success Rate"
            value={`${dashboardMetrics.email_success_rate}%`}
            subtitle="Notification delivery"
            icon={Mail}
            trend={[85, 88, 92, 95, 98, 99, 100]}
          />
          
          <MetricCard
            title="Active Jobs"
            value={dashboardMetrics.active_jobs}
            subtitle="Scheduled tasks"
            icon={Calendar}
            trend={[3, 4, 5, 6, 5, 4, 3]}
          />
          
          <MetricCard
            title="Uptime"
            value="99.9%"
            subtitle="Service availability"
            icon={Server}
            trend={[99, 100, 99, 98, 100, 99, 100]}
          />
        </div>

        {/* Ticker Analysis Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Quick Analysis</h3>
            <Target className="w-5 h-5 text-gray-400" />
          </div>
          
          <div className="flex items-center space-x-4">
            <input
              type="text"
              placeholder="Enter ticker symbol (e.g., AAPL)"
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value.toUpperCase())}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={() => handleTickerAnalysis(selectedTicker)}
              disabled={!selectedTicker || analyzeTicker.isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {analyzeTicker.isLoading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
          
          {analyzeTicker.error && (
            <ErrorMessage 
              message={analyzeTicker.error as string} 
              className="mt-4" 
            />
          )}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* System Status */}
          <div className="lg:col-span-1">
            {systemStatusLoading ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <LoadingSpinner />
              </div>
            ) : systemStatus?.data ? (
              <SystemStatusCard status={systemStatus.data} />
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <ErrorMessage message="Failed to load system status" />
              </div>
            )}
          </div>

          {/* Recent Events */}
          <div className="lg:col-span-1">
            {eventsLoading ? (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <LoadingSpinner />
              </div>
            ) : events ? (
              <EventsCard 
                events={events.events || []} 
                totalCount={events.total_count || 0}
                onFilterChange={updateFilter}
                maxEvents={5}
              />
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <ErrorMessage message="Failed to load events" />
              </div>
            )}
          </div>
        </div>

        {/* Insights Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Insights</h3>
            <div className="flex items-center space-x-2">
              <Brain className="w-5 h-5 text-gray-400" />
              <span className="text-sm text-gray-600">
                {insights?.total_count || 0} insights
              </span>
            </div>
          </div>

          {insightsLoading ? (
            <LoadingSpinner />
          ) : insights?.insights && insights.insights.length > 0 ? (
            <div className="space-y-4">
              {insights.insights.slice(0, 6).map((insight, index) => (
                <div key={insight.id || index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="font-medium text-gray-900">{insight.ticker}</span>
                        {insight.impact_level && (
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(insight.impact_level)}`}>
                            {insight.impact_level}
                          </span>
                        )}
                        {insight.confidence && (
                          <span className="text-xs text-gray-500">
                            {Math.round(insight.confidence * 100)}% confidence
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-700 mb-2">{insight.insight}</p>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>{formatDate(insight.timestamp)}</span>
                        <span className="flex items-center">
                          <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                          {insight.agent}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Brain className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No insights available</p>
            </div>
          )}
        </div>

        {/* Knowledge Evolution Preview */}
        {knowledgeEvolution?.data && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Knowledge Evolution</h3>
              <Globe className="w-5 h-5 text-gray-400" />
            </div>
            <div className="text-sm text-gray-700">
              <p className="mb-2">{knowledgeEvolution.data.evolution_info}</p>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <span>Trend: {knowledgeEvolution.data.improvement_trend}</span>
                {knowledgeEvolution.data.current_quality && (
                  <span>Quality: {Math.round(knowledgeEvolution.data.current_quality * 100)}%</span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default EnhancedDashboard; 