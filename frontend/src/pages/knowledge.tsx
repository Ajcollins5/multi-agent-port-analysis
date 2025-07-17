import React, { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { useKnowledgeEvolution } from '@/hooks/useApi';
import { POPULAR_STOCKS, formatDate } from '@/utils/api';
import { 
  Brain, 
  Timeline, 
  BookOpen, 
  TrendingUp,
  ChevronRight,
  Calendar,
  Lightbulb,
  ArrowRight,
  Clock,
  BarChart3
} from 'lucide-react';

const KnowledgeEvolution: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const { evolutionData, isLoading, fetchEvolution } = useKnowledgeEvolution(selectedTicker);

  const handleTickerChange = (ticker: string) => {
    setSelectedTicker(ticker);
    fetchEvolution(ticker);
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Knowledge Evolution</h1>
          <p className="text-gray-600">Track how AI understanding evolves over time</p>
        </div>

        {/* Ticker Selection */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Ticker for Evolution Analysis
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
                {POPULAR_STOCKS.slice(0, 12).map((stock) => (
                  <button
                    key={stock.ticker}
                    onClick={() => handleTickerChange(stock.ticker)}
                    className={`p-3 text-left border rounded-lg transition-colors ${
                      selectedTicker === stock.ticker
                        ? 'border-primary-300 bg-primary-50 text-primary-700'
                        : 'border-gray-200 hover:bg-gray-50 hover:border-primary-300'
                    }`}
                  >
                    <div className="text-sm font-medium text-gray-900">{stock.ticker}</div>
                    <div className="text-xs text-gray-500">{stock.sector}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom ticker input */}
            <div className="flex items-center space-x-2">
              <input
                type="text"
                placeholder="Or enter custom ticker..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    const target = e.target as HTMLInputElement;
                    const ticker = target.value.trim().toUpperCase();
                    if (ticker) {
                      handleTickerChange(ticker);
                      target.value = '';
                    }
                  }
                }}
              />
              <button
                onClick={() => {
                  const input = document.querySelector('input[placeholder="Or enter custom ticker..."]') as HTMLInputElement;
                  const ticker = input?.value.trim().toUpperCase();
                  if (ticker) {
                    handleTickerChange(ticker);
                    input.value = '';
                  }
                }}
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Analyze
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="bg-white rounded-lg border border-gray-200 p-8">
            <LoadingSpinner size="lg" text={`Loading knowledge evolution for ${selectedTicker}...`} />
          </div>
        )}

        {/* Evolution Summary */}
        {evolutionData && !isLoading && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Brain className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  Evolution Summary for {evolutionData.ticker}
                </h3>
                <p className="text-sm text-gray-500">How AI understanding has developed</p>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-800">{evolutionData.evolution_info}</p>
            </div>
          </div>
        )}

        {/* Historical Insights */}
        {evolutionData && !isLoading && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <BookOpen className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-medium text-gray-900">Historical Insights</h3>
              </div>
              <p className="text-sm text-gray-500 mt-1">Key learnings and improvements over time</p>
            </div>
            
            <div className="p-6">
              <div className="space-y-4">
                {evolutionData.historical_insights.map((insight: string, index: number) => (
                  <div key={index} className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-8 h-8 bg-success-100 rounded-full flex items-center justify-center">
                        <Lightbulb className="w-4 h-4 text-success-600" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-700">{insight}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Knowledge Timeline */}
        {evolutionData && !isLoading && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center space-x-2">
                <Timeline className="w-5 h-5 text-gray-600" />
                <h3 className="text-lg font-medium text-gray-900">Knowledge Timeline</h3>
              </div>
              <p className="text-sm text-gray-500 mt-1">Chronological development of understanding</p>
            </div>
            
            <div className="p-6">
              <div className="space-y-6">
                {evolutionData.timeline.map((timepoint: any, index: number) => (
                  <div key={index} className="relative">
                    {/* Timeline connector */}
                    {index < evolutionData.timeline.length - 1 && (
                      <div className="absolute left-4 top-10 w-0.5 h-16 bg-gray-200"></div>
                    )}
                    
                    <div className="flex items-start space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                          <Calendar className="w-4 h-4 text-primary-600" />
                        </div>
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="text-sm font-medium text-gray-900">
                            {formatDate(timepoint.date)}
                          </h4>
                          <span className="text-xs text-gray-500">
                            {timepoint.insights.length} insight{timepoint.insights.length !== 1 ? 's' : ''}
                          </span>
                        </div>
                        
                        <div className="space-y-2">
                          {timepoint.insights.map((insight: string, insightIndex: number) => (
                            <div key={insightIndex} className="flex items-start space-x-2">
                              <ArrowRight className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" />
                              <p className="text-sm text-gray-600">{insight}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Evolution Statistics */}
        {evolutionData && !isLoading && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-6 h-6 text-primary-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {evolutionData.timeline.length}
              </div>
              <div className="text-sm text-gray-500">Timeline Events</div>
            </div>
            
            <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Lightbulb className="w-6 h-6 text-success-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {evolutionData.historical_insights.length}
              </div>
              <div className="text-sm text-gray-500">Historical Insights</div>
            </div>
            
            <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
              <div className="w-12 h-12 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-6 h-6 text-warning-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {evolutionData.timeline.reduce((total: number, timepoint: any) => total + timepoint.insights.length, 0)}
              </div>
              <div className="text-sm text-gray-500">Total Insights</div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-purple-900 mb-2">Understanding Knowledge Evolution</h3>
          <ul className="text-sm text-purple-800 space-y-1">
            <li>• Knowledge evolution tracks how AI understanding improves over time</li>
            <li>• Each analysis refines the AI's understanding of market patterns</li>
            <li>• Historical insights show key learnings and improvements</li>
            <li>• The timeline visualizes chronological development of insights</li>
            <li>• Select different tickers to explore varying evolution patterns</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
};

export default KnowledgeEvolution; 