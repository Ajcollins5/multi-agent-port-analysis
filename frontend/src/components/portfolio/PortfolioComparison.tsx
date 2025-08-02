import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { 
  GitCompare, 
  TrendingUp, 
  TrendingDown, 
  BarChart3,
  Target,
  Shield,
  Zap,
  Plus,
  X
} from 'lucide-react';
import toast from 'react-hot-toast';

interface Portfolio {
  id: string;
  name: string;
  tickers: string[];
  color: string;
}

interface ComparisonResult {
  portfolios: Array<{
    name: string;
    tickers: string[];
    metrics: {
      expected_return: number;
      volatility: number;
      sharpe_ratio: number;
      max_drawdown: number;
      diversification_score: number;
    };
    insights: string[];
  }>;
  recommendation: string;
  best_portfolio: string;
}

const PortfolioComparison: React.FC = () => {
  const [portfolios, setPortfolios] = useState<Portfolio[]>([
    {
      id: '1',
      name: 'Growth Portfolio',
      tickers: ['AAPL', 'GOOGL', 'MSFT', 'AMZN'],
      color: 'blue'
    },
    {
      id: '2',
      name: 'Value Portfolio',
      tickers: ['BRK-B', 'JPM', 'JNJ', 'PG'],
      color: 'green'
    }
  ]);

  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [newPortfolioTickers, setNewPortfolioTickers] = useState('');

  const comparisonMutation = useMutation({
    mutationFn: async (portfolios: Portfolio[]) => {
      const response = await fetch('/api/portfolio/compare', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ portfolios }),
      });
      
      if (!response.ok) {
        throw new Error(`Comparison failed: ${response.statusText}`);
      }
      
      return response.json() as Promise<ComparisonResult>;
    },
    onSuccess: () => {
      toast.success('Portfolio comparison completed');
    },
    onError: (error) => {
      toast.error(`Comparison failed: ${error.message}`);
    },
  });

  const addPortfolio = () => {
    if (!newPortfolioName || !newPortfolioTickers) {
      toast.error('Please provide portfolio name and tickers');
      return;
    }

    const tickers = newPortfolioTickers
      .split(',')
      .map(t => t.trim().toUpperCase())
      .filter(t => t.length > 0);

    if (tickers.length === 0) {
      toast.error('Please provide valid tickers');
      return;
    }

    const colors = ['purple', 'orange', 'red', 'indigo', 'pink'];
    const newPortfolio: Portfolio = {
      id: Date.now().toString(),
      name: newPortfolioName,
      tickers,
      color: colors[portfolios.length % colors.length]
    };

    setPortfolios([...portfolios, newPortfolio]);
    setNewPortfolioName('');
    setNewPortfolioTickers('');
    toast.success('Portfolio added');
  };

  const removePortfolio = (id: string) => {
    setPortfolios(portfolios.filter(p => p.id !== id));
    toast.success('Portfolio removed');
  };

  const runComparison = () => {
    if (portfolios.length < 2) {
      toast.error('Please add at least 2 portfolios to compare');
      return;
    }
    comparisonMutation.mutate(portfolios);
  };

  const getColorClasses = (color: string) => {
    const colorMap: Record<string, string> = {
      blue: 'bg-blue-50 border-blue-200 text-blue-800',
      green: 'bg-green-50 border-green-200 text-green-800',
      purple: 'bg-purple-50 border-purple-200 text-purple-800',
      orange: 'bg-orange-50 border-orange-200 text-orange-800',
      red: 'bg-red-50 border-red-200 text-red-800',
      indigo: 'bg-indigo-50 border-indigo-200 text-indigo-800',
      pink: 'bg-pink-50 border-pink-200 text-pink-800'
    };
    return colorMap[color] || colorMap.blue;
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
        <GitCompare className="w-5 h-5 text-purple-600" />
        Portfolio Comparison
      </h2>

      {/* Add New Portfolio */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Add Portfolio</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input
            type="text"
            value={newPortfolioName}
            onChange={(e) => setNewPortfolioName(e.target.value)}
            placeholder="Portfolio name"
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <input
            type="text"
            value={newPortfolioTickers}
            onChange={(e) => setNewPortfolioTickers(e.target.value)}
            placeholder="Tickers (comma-separated)"
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            onClick={addPortfolio}
            className="flex items-center justify-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add
          </button>
        </div>
      </div>

      {/* Current Portfolios */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Current Portfolios ({portfolios.length})</h3>
        <div className="space-y-3">
          {portfolios.map((portfolio) => (
            <div key={portfolio.id} className={`p-3 rounded-lg border ${getColorClasses(portfolio.color)}`}>
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium">{portfolio.name}</h4>
                  <p className="text-sm opacity-75">
                    {portfolio.tickers.join(', ')} ({portfolio.tickers.length} assets)
                  </p>
                </div>
                <button
                  onClick={() => removePortfolio(portfolio.id)}
                  className="p-1 hover:bg-white hover:bg-opacity-50 rounded transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Comparison Controls */}
      <div className="mb-6">
        <button
          onClick={runComparison}
          disabled={comparisonMutation.isPending || portfolios.length < 2}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          <GitCompare className="w-4 h-4" />
          {comparisonMutation.isPending ? 'Comparing...' : 'Compare Portfolios'}
        </button>
      </div>

      {/* Comparison Results */}
      {comparisonMutation.data && (
        <div className="space-y-6">
          <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
            <h3 className="font-semibold text-green-900 mb-2">Recommendation</h3>
            <p className="text-green-800">{comparisonMutation.data.recommendation}</p>
            <p className="text-sm text-green-700 mt-1">
              Best performing: <strong>{comparisonMutation.data.best_portfolio}</strong>
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {comparisonMutation.data.portfolios.map((portfolio, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <h3 className="font-semibold text-gray-900 mb-3">{portfolio.name}</h3>
                
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Expected Return</span>
                    <span className="font-medium text-green-600">
                      {(portfolio.metrics.expected_return * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Volatility</span>
                    <span className="font-medium text-orange-600">
                      {(portfolio.metrics.volatility * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Sharpe Ratio</span>
                    <span className="font-medium text-blue-600">
                      {portfolio.metrics.sharpe_ratio.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Max Drawdown</span>
                    <span className="font-medium text-red-600">
                      {(portfolio.metrics.max_drawdown * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Diversification</span>
                    <span className="font-medium text-purple-600">
                      {(portfolio.metrics.diversification_score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Key Insights</h4>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {portfolio.insights.map((insight, i) => (
                      <li key={i}>• {insight}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioComparison;
