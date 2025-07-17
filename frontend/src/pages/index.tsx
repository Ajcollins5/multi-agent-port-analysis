import React, { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { MetricCard } from '@/components/common/MetricCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { usePortfolioData, useInsights } from '@/hooks/useApi';
import { formatCurrency, formatDate, getRiskColor, getImpactColor } from '@/utils/api';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  AlertTriangle,
  DollarSign,
  BarChart3,
  RefreshCw
} from 'lucide-react';

const PortfolioDashboard: React.FC = () => {
  const { data: portfolioData, isLoading: portfolioLoading, error: portfolioError, refetch: refetchPortfolio } = usePortfolioData();
  const { data: insightsData, isLoading: insightsLoading, error: insightsError, refetch: refetchInsights } = useInsights();
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([refetchPortfolio(), refetchInsights()]);
    setRefreshing(false);
  };

  const portfolio = portfolioData?.data;
  const insights = insightsData?.data;

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Portfolio Dashboard</h1>
            <p className="text-gray-600">Real-time portfolio analysis and insights</p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Portfolio Overview Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Total Stocks"
            value={portfolio?.portfolio_size || 0}
            icon={BarChart3}
            subtitle="Active positions"
          />
          <MetricCard
            title="High Impact"
            value={portfolio?.high_impact_count || 0}
            icon={AlertTriangle}
            subtitle="Stocks with volatility >5%"
            changeType={portfolio?.high_impact_count > 0 ? 'negative' : 'positive'}
          />
          <MetricCard
            title="Portfolio Risk"
            value={portfolio?.portfolio_risk || 'LOW'}
            icon={Activity}
            subtitle="Overall risk assessment"
            className={portfolio?.portfolio_risk ? getRiskColor(portfolio.portfolio_risk) : ''}
          />
          <MetricCard
            title="Analyzed Stocks"
            value={portfolio?.analyzed_stocks || 0}
            icon={TrendingUp}
            subtitle="Successfully analyzed"
          />
        </div>

        {/* Portfolio Error */}
        {portfolioError && (
          <ErrorMessage
            title="Portfolio Data Error"
            message={portfolioError?.message || 'Failed to load portfolio data'}
            onRetry={refetchPortfolio}
          />
        )}

        {/* Portfolio Results Table */}
        {portfolioLoading ? (
          <div className="bg-white rounded-lg border border-gray-200 p-8">
            <LoadingSpinner size="lg" text="Loading portfolio data..." />
          </div>
        ) : portfolio?.results && portfolio.results.length > 0 ? (
          <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Portfolio Holdings</h3>
              <p className="text-sm text-gray-500">Current stock positions and analysis</p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ticker
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Volatility
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Impact Level
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Updated
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {portfolio.results.map((stock) => (
                    <tr key={stock.ticker} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900">{stock.ticker}</div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {formatCurrency(stock.current_price)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">
                          {(stock.volatility * 100).toFixed(2)}%
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full border ${getImpactColor(stock.impact_level)}`}>
                          {stock.impact_level}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {stock.high_impact ? (
                            <div className="flex items-center space-x-1 text-error-600">
                              <AlertTriangle className="w-4 h-4" />
                              <span className="text-xs">High Impact</span>
                            </div>
                          ) : (
                            <div className="flex items-center space-x-1 text-success-600">
                              <Activity className="w-4 h-4" />
                              <span className="text-xs">Normal</span>
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(stock.timestamp)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg border border-gray-200 p-8 text-center">
            <BarChart3 className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-4 text-lg font-medium text-gray-900">No portfolio data</h3>
            <p className="mt-2 text-sm text-gray-500">
              Portfolio analysis will appear here once analysis is complete.
            </p>
          </div>
        )}

        {/* Recent Insights */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Insights</h3>
            <p className="text-sm text-gray-500">Latest AI-generated market analysis</p>
          </div>
          
          {insightsError && (
            <div className="p-6">
              <ErrorMessage
                title="Insights Error"
                message={insightsError?.message || 'Failed to load insights'}
                onRetry={refetchInsights}
              />
            </div>
          )}
          
          {insightsLoading ? (
            <div className="p-8">
              <LoadingSpinner size="lg" text="Loading insights..." />
            </div>
          ) : insights?.insights && insights.insights.length > 0 ? (
            <div className="divide-y divide-gray-200">
              {insights.insights.slice(0, 5).map((insight, index) => (
                <div key={index} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                        <TrendingUp className="w-5 h-5 text-primary-600" />
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <h4 className="text-sm font-medium text-gray-900">{insight.ticker}</h4>
                        <span className="text-sm text-gray-500">{formatDate(insight.timestamp)}</span>
                      </div>
                      <p className="mt-1 text-sm text-gray-600">{insight.insight}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center">
              <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">No insights yet</h3>
              <p className="mt-2 text-sm text-gray-500">
                AI-generated insights will appear here after analysis.
              </p>
            </div>
          )}
        </div>

        {/* Portfolio Summary */}
        {portfolio && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">{portfolio.portfolio_size}</div>
                <div className="text-sm text-gray-500">Total Holdings</div>
              </div>
              <div className="text-center">
                <div className={`text-2xl font-bold ${getRiskColor(portfolio.portfolio_risk).split(' ')[0]}`}>
                  {portfolio.portfolio_risk}
                </div>
                <div className="text-sm text-gray-500">Risk Level</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {insights?.total_count || 0}
                </div>
                <div className="text-sm text-gray-500">Total Insights</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default PortfolioDashboard; 