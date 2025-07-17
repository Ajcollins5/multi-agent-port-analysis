import React, { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { MetricCard } from '@/components/common/MetricCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { useAnalyzeTicker } from '@/hooks/useApi';
import { POPULAR_STOCKS, formatCurrency, formatDate, getImpactColor } from '@/utils/api';
import { 
  Search, 
  TrendingUp, 
  AlertTriangle,
  Activity,
  DollarSign,
  BarChart3,
  Clock,
  Mail,
  Star
} from 'lucide-react';

const AdHocAnalysis: React.FC = () => {
  const [ticker, setTicker] = useState('');
  const [analysisHistory, setAnalysisHistory] = useState<any[]>([]);
  const analyzeTicker = useAnalyzeTicker();

  const handleAnalyze = async (symbolToAnalyze?: string) => {
    const symbol = symbolToAnalyze || ticker.trim().toUpperCase();
    
    if (!symbol) {
      return;
    }

    const result = await analyzeTicker.mutateAsync(symbol);
    
    if (result.success && result.data) {
      // Add to history
      setAnalysisHistory(prev => [
        {
          ...result.data,
          timestamp: new Date().toISOString()
        },
        ...prev.slice(0, 9) // Keep last 10 analyses
      ]);
    }

    // Clear input if it was manually typed
    if (!symbolToAnalyze) {
      setTicker('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleAnalyze();
    }
  };

  const currentAnalysis = analyzeTicker.data?.data;
  const isLoading = analyzeTicker.isLoading;
  const error = analyzeTicker.error;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Ad-hoc Analysis</h1>
          <p className="text-gray-600">Analyze individual stocks with AI-powered insights</p>
        </div>

        {/* Analysis Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="space-y-4">
            <div>
              <label htmlFor="ticker" className="block text-sm font-medium text-gray-700 mb-2">
                Enter Ticker Symbol
              </label>
              <div className="flex space-x-3">
                <div className="flex-1">
                  <input
                    id="ticker"
                    type="text"
                    value={ticker}
                    onChange={(e) => setTicker(e.target.value.toUpperCase())}
                    onKeyPress={handleKeyPress}
                    placeholder="e.g., AAPL, GOOGL, TSLA"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    disabled={isLoading}
                  />
                </div>
                <button
                  onClick={() => handleAnalyze()}
                  disabled={isLoading || !ticker.trim()}
                  className="px-6 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {isLoading ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <Search className="w-4 h-4" />
                  )}
                  <span>Analyze</span>
                </button>
              </div>
            </div>

            {/* Popular Stocks */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quick Analysis - Popular Stocks
              </label>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                {POPULAR_STOCKS.slice(0, 15).map((stock) => (
                  <button
                    key={stock.ticker}
                    onClick={() => handleAnalyze(stock.ticker)}
                    disabled={isLoading}
                    className="p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-primary-300 disabled:opacity-50 transition-colors"
                  >
                    <div className="flex items-center space-x-2">
                      <Star className="w-4 h-4 text-yellow-500" />
                      <div>
                        <div className="text-sm font-medium text-gray-900">{stock.ticker}</div>
                        <div className="text-xs text-gray-500">{stock.sector}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Analysis Error */}
        {error && (
          <ErrorMessage
            title="Analysis Error"
            message={error?.message || 'Failed to analyze ticker'}
            onRetry={() => handleAnalyze()}
          />
        )}

        {/* Current Analysis Results */}
        {currentAnalysis && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-medium text-gray-900">
                Analysis Results for {currentAnalysis.ticker}
              </h3>
              {currentAnalysis.email_sent && (
                <div className="flex items-center space-x-2 text-success-600">
                  <Mail className="w-4 h-4" />
                  <span className="text-sm">Email sent</span>
                </div>
              )}
            </div>

            {/* Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <MetricCard
                title="Current Price"
                value={formatCurrency(currentAnalysis.current_price)}
                icon={DollarSign}
                subtitle="Real-time price"
              />
              <MetricCard
                title="Volatility"
                value={`${(currentAnalysis.volatility * 100).toFixed(2)}%`}
                icon={Activity}
                subtitle="Price volatility"
                changeType={currentAnalysis.volatility > 0.05 ? 'negative' : 'positive'}
              />
              <MetricCard
                title="Impact Level"
                value={currentAnalysis.impact_level}
                icon={AlertTriangle}
                subtitle="Risk assessment"
                className={getImpactColor(currentAnalysis.impact_level)}
              />
              <MetricCard
                title="High Impact"
                value={currentAnalysis.high_impact ? 'YES' : 'NO'}
                icon={currentAnalysis.high_impact ? AlertTriangle : Activity}
                subtitle="Alert status"
                changeType={currentAnalysis.high_impact ? 'negative' : 'positive'}
              />
            </div>

            {/* High Impact Alert */}
            {currentAnalysis.high_impact && (
              <div className="bg-error-50 border border-error-200 rounded-lg p-4 mb-6">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-error-600" />
                  <h4 className="text-sm font-medium text-error-800">High Impact Event Detected</h4>
                </div>
                                 <p className="text-sm text-error-700 mt-1">
                   {currentAnalysis.ticker} is showing high volatility (&gt;{(currentAnalysis.volatility * 100).toFixed(2)}%). 
                   {currentAnalysis.email_sent && ' Email notification has been sent.'}
                 </p>
              </div>
            )}
          </div>
        )}

        {/* Analysis History */}
        {analysisHistory.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Analysis History</h3>
              <p className="text-sm text-gray-500">Recent stock analyses</p>
            </div>
            <div className="divide-y divide-gray-200">
              {analysisHistory.map((analysis, index) => (
                <div key={index} className="p-6 hover:bg-gray-50">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex-shrink-0">
                        <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                          <BarChart3 className="w-5 h-5 text-primary-600" />
                        </div>
                      </div>
                      <div>
                        <h4 className="text-sm font-medium text-gray-900">{analysis.ticker}</h4>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>{formatCurrency(analysis.current_price)}</span>
                          <span>Volatility: {(analysis.volatility * 100).toFixed(2)}%</span>
                          <span className={`px-2 py-1 text-xs rounded-full ${getImpactColor(analysis.impact_level)}`}>
                            {analysis.impact_level}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <Clock className="w-4 h-4" />
                      <span>{formatDate(analysis.timestamp)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-2">How to Use</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Enter a ticker symbol (e.g., AAPL, GOOGL) and click Analyze</li>
            <li>• Or click on any popular stock button for quick analysis</li>
                         <li>• High impact events (volatility &gt;5%) will trigger email notifications</li>
            <li>• All analyses are powered by AI agents with real-time market data</li>
            <li>• Results include current price, volatility, and risk assessment</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
};

export default AdHocAnalysis; 