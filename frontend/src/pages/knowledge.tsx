import React, { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { MetricCard } from '@/components/common/MetricCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { 
  useKnowledgeEvolution, 
  useKnowledgeQuality, 
  useKnowledgeGaps,
  useQualityEvolution,
  useAdvancedFilters
} from '@/hooks/useApi';
import { formatDate, formatShortDate, getImpactColor } from '@/utils/api';
import { 
  Brain, 
  Target, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Search,
  Filter,
  Clock,
  BarChart3,
  Activity,
  Globe,
  Zap
} from 'lucide-react';

const KnowledgePage: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState('');
  const [timeWindow, setTimeWindow] = useState(24);
  
  // Advanced filters
  const { filters, updateFilter, resetFilters } = useAdvancedFilters();
  
  // Knowledge data hooks
  const { data: knowledgeEvolution, isLoading: evolutionLoading, error: evolutionError } = useKnowledgeEvolution({
    ...filters,
    ticker: selectedTicker || undefined
  });
  
  const { data: knowledgeQuality, isLoading: qualityLoading, error: qualityError } = useKnowledgeQuality();
  const { data: knowledgeGaps, isLoading: gapsLoading, error: gapsError } = useKnowledgeGaps(timeWindow);
  const { data: qualityEvolution, isLoading: qualityEvolutionLoading, error: qualityEvolutionError } = useQualityEvolution();

  const isLoading = evolutionLoading || qualityLoading || gapsLoading || qualityEvolutionLoading;
  const hasError = evolutionError || qualityError || gapsError || qualityEvolutionError;

  const getGapSeverityColor = (severity: string) => {
    switch (severity?.toUpperCase()) {
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

  const getTrendIcon = (trend: string) => {
    switch (trend?.toLowerCase()) {
      case 'improving':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'declining':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Knowledge Base</h1>
            <p className="text-gray-600">
              AI knowledge evolution and quality assessment
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <Brain className="w-6 h-6 text-blue-600" />
          </div>
        </div>

        {/* Quick Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Filters</h3>
            <Filter className="w-5 h-5 text-gray-400" />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ticker Symbol
              </label>
              <input
                type="text"
                placeholder="e.g., AAPL"
                value={selectedTicker}
                onChange={(e) => setSelectedTicker(e.target.value.toUpperCase())}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Time Window (hours)
              </label>
              <select
                value={timeWindow}
                onChange={(e) => setTimeWindow(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value={24}>Last 24 hours</option>
                <option value={72}>Last 3 days</option>
                <option value={168}>Last week</option>
                <option value={720}>Last month</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <button
                onClick={resetFilters}
                className="w-full px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                Reset Filters
              </button>
            </div>
          </div>
        </div>

        {/* Knowledge Quality Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Overall Quality"
            value={knowledgeQuality?.data?.overall_score ? `${Math.round(knowledgeQuality.data.overall_score * 100)}%` : 'N/A'}
            subtitle="Knowledge base quality"
            icon={<Target className="w-5 h-5" />}
            trend={[65, 70, 75, 80, 85, 88, 92]}
          />
          
          <MetricCard
            title="Completeness"
            value={knowledgeQuality?.data?.quality_metrics?.completeness ? `${Math.round(knowledgeQuality.data.quality_metrics.completeness * 100)}%` : 'N/A'}
            subtitle="Data completeness"
            icon={<CheckCircle className="w-5 h-5" />}
            trend={[60, 65, 70, 75, 80, 85, 90]}
          />
          
          <MetricCard
            title="Timeliness"
            value={knowledgeQuality?.data?.quality_metrics?.timeliness ? `${Math.round(knowledgeQuality.data.quality_metrics.timeliness * 100)}%` : 'N/A'}
            subtitle="Data freshness"
            icon={<Clock className="w-5 h-5" />}
            trend={[70, 75, 80, 85, 90, 95, 98]}
          />
          
          <MetricCard
            title="Knowledge Gaps"
            value={knowledgeGaps?.data?.gaps?.length || 0}
            subtitle="Identified gaps"
            icon={<AlertTriangle className="w-5 h-5" />}
            trend={[15, 12, 10, 8, 6, 4, 2]}
          />
        </div>

        {/* Knowledge Evolution */}
        {knowledgeEvolution?.data && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Knowledge Evolution</h3>
              <div className="flex items-center space-x-2">
                <Globe className="w-5 h-5 text-gray-400" />
                {getTrendIcon(knowledgeEvolution.data.improvement_trend)}
                <span className="text-sm text-gray-600 capitalize">
                  {knowledgeEvolution.data.improvement_trend}
                </span>
              </div>
            </div>
            
            <div className="mb-4">
              <div className="flex items-center space-x-2 mb-2">
                <span className="font-medium text-gray-900">
                  {knowledgeEvolution.data.ticker}
                </span>
                <span className="text-sm text-gray-500">
                  {knowledgeEvolution.data.evolution_type}
                </span>
                <span className="text-sm text-gray-500">
                  by {knowledgeEvolution.data.agent}
                </span>
              </div>
              <p className="text-sm text-gray-700 mb-4">
                {knowledgeEvolution.data.evolution_info}
              </p>
              
              {knowledgeEvolution.data.current_quality && (
                <div className="flex items-center space-x-2 mb-4">
                  <span className="text-sm text-gray-600">Current Quality:</span>
                  <span className="font-medium text-gray-900">
                    {Math.round(knowledgeEvolution.data.current_quality * 100)}%
                  </span>
                </div>
              )}
            </div>
            
            {/* Historical Insights */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Recent Insights</h4>
              <div className="space-y-2">
                {knowledgeEvolution.data.historical_insights.map((insight, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                    <p className="text-sm text-gray-700">{insight}</p>
                  </div>
                ))}
              </div>
            </div>
            
            {/* Timeline */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Evolution Timeline</h4>
              <div className="space-y-3">
                {knowledgeEvolution.data.timeline.map((item, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-xs font-medium text-blue-600">
                          {index + 1}
                        </span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-sm font-medium text-gray-900">
                          {formatShortDate(item.date)}
                        </span>
                        {item.quality_score && (
                          <span className="text-xs text-gray-500">
                            Quality: {Math.round(item.quality_score * 100)}%
                          </span>
                        )}
                      </div>
                      <div className="space-y-1">
                        {item.insights.map((insight, insightIndex) => (
                          <p key={insightIndex} className="text-sm text-gray-600">
                            {insight}
                          </p>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Knowledge Gaps */}
        {knowledgeGaps?.data?.gaps && knowledgeGaps.data.gaps.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Knowledge Gaps</h3>
              <div className="flex items-center space-x-2">
                <AlertTriangle className="w-5 h-5 text-yellow-500" />
                <span className="text-sm text-gray-600">
                  {knowledgeGaps.data.gaps.length} gaps identified
                </span>
              </div>
            </div>
            
            <div className="space-y-4">
              {knowledgeGaps.data.gaps.map((gap, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-gray-900">{gap.type}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getGapSeverityColor(gap.severity)}`}>
                        {gap.severity}
                      </span>
                    </div>
                    {gap.agent && (
                      <span className="text-sm text-gray-500">{gap.agent}</span>
                    )}
                  </div>
                  
                  <p className="text-sm text-gray-700 mb-3">{gap.description}</p>
                  
                  {gap.recommendations && gap.recommendations.length > 0 && (
                    <div>
                      <h5 className="text-sm font-medium text-gray-700 mb-2">Recommendations:</h5>
                      <ul className="space-y-1">
                        {gap.recommendations.map((rec, recIndex) => (
                          <li key={recIndex} className="flex items-start space-x-2">
                            <Zap className="w-3 h-3 text-blue-500 mt-0.5 flex-shrink-0" />
                            <span className="text-sm text-gray-600">{rec}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quality Metrics Details */}
        {knowledgeQuality?.data && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Quality Metrics</h3>
              <BarChart3 className="w-5 h-5 text-gray-400" />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">Detailed Metrics</h4>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Completeness</span>
                    <span className="font-medium">
                      {Math.round(knowledgeQuality.data.quality_metrics.completeness * 100)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Accuracy</span>
                    <span className="font-medium">
                      {Math.round(knowledgeQuality.data.quality_metrics.accuracy * 100)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Timeliness</span>
                    <span className="font-medium">
                      {Math.round(knowledgeQuality.data.quality_metrics.timeliness * 100)}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Relevance</span>
                    <span className="font-medium">
                      {Math.round(knowledgeQuality.data.quality_metrics.relevance * 100)}%
                    </span>
                  </div>
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">Improvement Suggestions</h4>
                <div className="space-y-2">
                  {knowledgeQuality.data.improvement_suggestions.map((suggestion, index) => (
                    <div key={index} className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{suggestion}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading States */}
        {isLoading && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
            <LoadingSpinner size="lg" text="Loading knowledge data..." />
          </div>
        )}

        {/* Error States */}
        {hasError && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <ErrorMessage 
              title="Knowledge Data Error" 
              message="Failed to load knowledge data. Please try again." 
            />
          </div>
        )}
      </div>
    </Layout>
  );
};

export default KnowledgePage; 