import React, { useState, useEffect } from 'react';
import {
  Newspaper,
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  BarChart3,
  Brain,
  Zap,
  Calendar,
  Filter,
  History,
  Search,
  SortAsc,
  SortDesc,
  ExternalLink,
  Eye,
  X
} from 'lucide-react';

interface NewsSnapshot {
  ticker: string;
  timestamp: string;
  category: string;
  impact: string;
  price_change_1h: number;
  price_change_24h: number;
  summary_line_1: string;
  summary_line_2: string;
  source_url: string;
  confidence_score: number;
}

interface StockPersonality {
  ticker: string;
  total_events: number;
  avg_volatility: number;
  reaction_patterns: Record<string, any>;
  sentiment_sensitivity: number;
  news_momentum: number;
  last_updated: string;
}

const NewsIntelligenceDashboard: React.FC = () => {
  const [selectedTicker, setSelectedTicker] = useState('AAPL');
  const [newsHistory, setNewsHistory] = useState<NewsSnapshot[]>([]);
  const [stockPersonality, setStockPersonality] = useState<StockPersonality | null>(null);
  const [timeRange, setTimeRange] = useState(90); // days
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  // History tab specific state
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'timestamp' | 'impact' | 'confidence'>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [impactFilter, setImpactFilter] = useState('all');
  const [selectedEvent, setSelectedEvent] = useState<NewsSnapshot | null>(null);

  // Extended mock data for demonstration
  const mockNewsSnapshots: NewsSnapshot[] = [
    {
      ticker: 'AAPL',
      timestamp: '2024-01-15T10:30:00Z',
      category: 'earnings',
      impact: 'positive',
      price_change_1h: 2.1,
      price_change_24h: 3.4,
      summary_line_1: 'AAPL reported quarterly earnings with key metrics showing strong performance.',
      summary_line_2: 'The stock rose 3.4% in 24 hours as investors embraced the news.',
      source_url: 'https://example.com/news/1',
      confidence_score: 0.87
    },
    {
      ticker: 'AAPL',
      timestamp: '2024-01-10T14:15:00Z',
      category: 'product_launch',
      impact: 'very_positive',
      price_change_1h: 1.8,
      price_change_24h: 5.2,
      summary_line_1: 'AAPL announced a new product launch that exceeded market expectations.',
      summary_line_2: 'The stock surged 5.2% in 24 hours as investors embraced the news.',
      source_url: 'https://example.com/news/2',
      confidence_score: 0.92
    },
    {
      ticker: 'AAPL',
      timestamp: '2024-01-05T09:45:00Z',
      category: 'analyst_rating',
      impact: 'negative',
      price_change_1h: -1.2,
      price_change_24h: -2.8,
      summary_line_1: 'AAPL received analyst downgrade that negatively impacts its business prospects.',
      summary_line_2: 'The stock fell 2.8% in 24 hours as investors rejected the news.',
      source_url: 'https://example.com/news/3',
      confidence_score: 0.75
    },
    {
      ticker: 'AAPL',
      timestamp: '2023-12-20T11:20:00Z',
      category: 'regulatory',
      impact: 'very_negative',
      price_change_1h: -3.1,
      price_change_24h: -6.8,
      summary_line_1: 'AAPL faces new regulatory challenges that could impact future revenue streams.',
      summary_line_2: 'The stock plummeted 6.8% in 24 hours as investors rejected the news.',
      source_url: 'https://example.com/news/4',
      confidence_score: 0.91
    },
    {
      ticker: 'AAPL',
      timestamp: '2023-12-15T16:45:00Z',
      category: 'partnership',
      impact: 'positive',
      price_change_1h: 1.4,
      price_change_24h: 2.9,
      summary_line_1: 'AAPL announced strategic partnership that opens new market opportunities.',
      summary_line_2: 'The stock rose 2.9% in 24 hours as investors embraced the news.',
      source_url: 'https://example.com/news/5',
      confidence_score: 0.83
    },
    {
      ticker: 'AAPL',
      timestamp: '2023-12-01T08:30:00Z',
      category: 'leadership',
      impact: 'neutral',
      price_change_1h: 0.2,
      price_change_24h: -0.5,
      summary_line_1: 'AAPL announced executive leadership changes in key business divisions.',
      summary_line_2: 'The stock fell 0.5% in 24 hours as investors rejected the news.',
      source_url: 'https://example.com/news/6',
      confidence_score: 0.68
    },
    {
      ticker: 'AAPL',
      timestamp: '2023-11-28T13:15:00Z',
      category: 'earnings',
      impact: 'very_positive',
      price_change_1h: 4.2,
      price_change_24h: 7.1,
      summary_line_1: 'AAPL reported quarterly earnings with key metrics showing strong performance.',
      summary_line_2: 'The stock surged 7.1% in 24 hours as investors embraced the news.',
      source_url: 'https://example.com/news/7',
      confidence_score: 0.94
    }
  ];

  const mockPersonality: StockPersonality = {
    ticker: 'AAPL',
    total_events: 47,
    avg_volatility: 2.8,
    reaction_patterns: {
      earnings: { avg_impact: 3.2, frequency: 0.25, volatility: 4.1 },
      product_launch: { avg_impact: 4.8, frequency: 0.15, volatility: 5.2 },
      analyst_rating: { avg_impact: -1.2, frequency: 0.30, volatility: 2.1 }
    },
    sentiment_sensitivity: 0.65,
    news_momentum: 0.72,
    last_updated: '2024-01-15T15:30:00Z'
  };

  useEffect(() => {
    setNewsHistory(mockNewsSnapshots);
    setStockPersonality(mockPersonality);
  }, [selectedTicker]);

  // Filter and sort news history
  const filteredAndSortedHistory = React.useMemo(() => {
    let filtered = newsHistory.filter(snapshot => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!snapshot.summary_line_1.toLowerCase().includes(query) &&
            !snapshot.summary_line_2.toLowerCase().includes(query) &&
            !snapshot.category.toLowerCase().includes(query)) {
          return false;
        }
      }

      // Category filter
      if (categoryFilter !== 'all' && snapshot.category !== categoryFilter) {
        return false;
      }

      // Impact filter
      if (impactFilter !== 'all' && snapshot.impact !== impactFilter) {
        return false;
      }

      return true;
    });

    // Sort
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;

      switch (sortBy) {
        case 'timestamp':
          aValue = new Date(a.timestamp).getTime();
          bValue = new Date(b.timestamp).getTime();
          break;
        case 'impact':
          const impactOrder = { very_negative: -2, negative: -1, neutral: 0, positive: 1, very_positive: 2 };
          aValue = impactOrder[a.impact as keyof typeof impactOrder];
          bValue = impactOrder[b.impact as keyof typeof impactOrder];
          break;
        case 'confidence':
          aValue = a.confidence_score;
          bValue = b.confidence_score;
          break;
        default:
          return 0;
      }

      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
    });

    return filtered;
  }, [newsHistory, searchQuery, categoryFilter, impactFilter, sortBy, sortOrder]);

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'very_positive': return 'text-green-700 bg-green-100';
      case 'positive': return 'text-green-600 bg-green-50';
      case 'neutral': return 'text-gray-600 bg-gray-50';
      case 'negative': return 'text-red-600 bg-red-50';
      case 'very_negative': return 'text-red-700 bg-red-100';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'earnings': return <BarChart3 className="w-4 h-4" />;
      case 'product_launch': return <Zap className="w-4 h-4" />;
      case 'analyst_rating': return <Target className="w-4 h-4" />;
      default: return <Newspaper className="w-4 h-4" />;
    }
  };

  const formatCategory = (category: string) => {
    return category.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Brain className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">News Intelligence</h1>
        </div>
        <p className="text-gray-600">
          Compressed news analysis showing how stocks react to events over time
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border mb-8">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4" />
                Overview & Personality
              </div>
            </button>

            <button
              onClick={() => setActiveTab('history')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'history'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <History className="w-4 h-4" />
                News History ({filteredAndSortedHistory.length})
              </div>
            </button>
          </nav>
        </div>

        {/* Controls */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Stock Ticker</label>
              <input
                type="text"
                value={selectedTicker}
                onChange={(e) => setSelectedTicker(e.target.value.toUpperCase())}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="AAPL"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Time Range</label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(Number(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={30}>30 Days</option>
                <option value={90}>90 Days</option>
                <option value={180}>6 Months</option>
                <option value={365}>1 Year</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">All Categories</option>
                <option value="earnings">Earnings</option>
                <option value="product_launch">Product Launch</option>
                <option value="analyst_rating">Analyst Rating</option>
                <option value="regulatory">Regulatory</option>
                <option value="partnership">Partnership</option>
                <option value="leadership">Leadership</option>
              </select>
            </div>

            <div className="flex items-end">
              <button
                onClick={() => setIsLoading(true)}
                className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Refresh Data
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Stock Personality Profile */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Brain className="w-5 h-5 text-purple-600" />
                Stock Personality
              </h2>

              {stockPersonality && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="text-center p-3 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{stockPersonality.total_events}</div>
                      <div className="text-xs text-gray-600">Total Events</div>
                    </div>
                    <div className="text-center p-3 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">{stockPersonality.avg_volatility.toFixed(1)}%</div>
                      <div className="text-xs text-gray-600">Avg Volatility</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-sm">
                        <span>Sentiment Sensitivity</span>
                        <span>{(stockPersonality.sentiment_sensitivity * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-purple-600 h-2 rounded-full"
                          style={{ width: `${stockPersonality.sentiment_sensitivity * 100}%` }}
                        ></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between text-sm">
                        <span>News Momentum</span>
                        <span>{(stockPersonality.news_momentum * 100).toFixed(0)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${stockPersonality.news_momentum * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>

                  <div className="text-xs text-gray-500">
                    Last updated: {new Date(stockPersonality.last_updated).toLocaleDateString()}
                  </div>
                </div>
              )}
            </div>

            {/* Reaction Patterns */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Reaction Patterns</h3>
              {stockPersonality && (
                <div className="space-y-3">
                  {Object.entries(stockPersonality.reaction_patterns).map(([category, pattern]: [string, any]) => (
                    <div key={category} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-2">
                        {getCategoryIcon(category)}
                        <span className="text-sm font-medium">{formatCategory(category)}</span>
                      </div>
                      <div className="text-right">
                        <div className={`text-sm font-medium ${pattern.avg_impact >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {pattern.avg_impact >= 0 ? '+' : ''}{pattern.avg_impact.toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-500">{(pattern.frequency * 100).toFixed(0)}% freq</div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Recent News Timeline */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Newspaper className="w-5 h-5 text-blue-600" />
                Recent News Timeline
              </h2>

              <div className="space-y-4 max-h-96 overflow-y-auto">
                {newsHistory.slice(0, 5).map((snapshot, index) => (
                  <div key={index} className="border-l-4 border-blue-200 pl-4 pb-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getCategoryIcon(snapshot.category)}
                        <span className="text-sm font-medium text-gray-600">
                          {formatCategory(snapshot.category)}
                        </span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(snapshot.impact)}`}>
                          {snapshot.impact.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(snapshot.timestamp).toLocaleDateString()}
                      </div>
                    </div>

                    <div className="space-y-1 mb-3">
                      <p className="text-sm text-gray-900">{snapshot.summary_line_1}</p>
                      <p className="text-sm text-gray-700">{snapshot.summary_line_2}</p>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-4">
                        <span className={`flex items-center gap-1 ${snapshot.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {snapshot.price_change_24h >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                          {snapshot.price_change_24h >= 0 ? '+' : ''}{snapshot.price_change_24h.toFixed(1)}% (24h)
                        </span>
                        <span className="text-gray-500">
                          Confidence: {(snapshot.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 text-center">
                <button
                  onClick={() => setActiveTab('history')}
                  className="px-4 py-2 text-blue-600 hover:text-blue-800 font-medium"
                >
                  View All {newsHistory.length} Events →
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* History Tab */}
      {activeTab === 'history' && (
        <div className="space-y-6">
          {/* History Controls */}
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {/* Search */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Search Events</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Search in summaries..."
                  />
                </div>
              </div>

              {/* Impact Filter */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Impact</label>
                <select
                  value={impactFilter}
                  onChange={(e) => setImpactFilter(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="all">All Impacts</option>
                  <option value="very_positive">Very Positive</option>
                  <option value="positive">Positive</option>
                  <option value="neutral">Neutral</option>
                  <option value="negative">Negative</option>
                  <option value="very_negative">Very Negative</option>
                </select>
              </div>

              {/* Sort By */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'timestamp' | 'impact' | 'confidence')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="timestamp">Date</option>
                  <option value="impact">Impact</option>
                  <option value="confidence">Confidence</option>
                </select>
              </div>

              {/* Sort Order */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Order</label>
                <button
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center justify-center gap-2"
                >
                  {sortOrder === 'asc' ? <SortAsc className="w-4 h-4" /> : <SortDesc className="w-4 h-4" />}
                  {sortOrder === 'asc' ? 'Ascending' : 'Descending'}
                </button>
              </div>
            </div>

            {/* Results Summary */}
            <div className="mt-4 flex items-center justify-between text-sm text-gray-600">
              <span>
                Showing {filteredAndSortedHistory.length} of {newsHistory.length} events
                {searchQuery && ` for "${searchQuery}"`}
              </span>
              {(searchQuery || categoryFilter !== 'all' || impactFilter !== 'all') && (
                <button
                  onClick={() => {
                    setSearchQuery('');
                    setCategoryFilter('all');
                    setImpactFilter('all');
                  }}
                  className="text-blue-600 hover:text-blue-800"
                >
                  Clear filters
                </button>
              )}
            </div>
          </div>

          {/* History List */}
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <History className="w-5 h-5 text-blue-600" />
                News Event History
              </h2>

              <div className="space-y-4">
                {filteredAndSortedHistory.map((snapshot, index) => (
                  <div
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => setSelectedEvent(snapshot)}
                  >
                    {/* Event Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-3">
                        {getCategoryIcon(snapshot.category)}
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-gray-900">
                              {formatCategory(snapshot.category)}
                            </span>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(snapshot.impact)}`}>
                              {snapshot.impact.replace('_', ' ').toUpperCase()}
                            </span>
                          </div>
                          <div className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                            <Clock className="w-3 h-3" />
                            {new Date(snapshot.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className="flex items-center gap-4 text-sm">
                          <div className={`flex items-center gap-1 font-medium ${snapshot.price_change_1h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {snapshot.price_change_1h >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {snapshot.price_change_1h >= 0 ? '+' : ''}{snapshot.price_change_1h.toFixed(1)}% (1h)
                          </div>
                          <div className={`flex items-center gap-1 font-medium ${snapshot.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {snapshot.price_change_24h >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {snapshot.price_change_24h >= 0 ? '+' : ''}{snapshot.price_change_24h.toFixed(1)}% (24h)
                          </div>
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          Confidence: {(snapshot.confidence_score * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>

                    {/* Event Summary */}
                    <div className="space-y-2">
                      <p className="text-sm text-gray-900 leading-relaxed">
                        <span className="font-medium">Event:</span> {snapshot.summary_line_1}
                      </p>
                      <p className="text-sm text-gray-700 leading-relaxed">
                        <span className="font-medium">Market Reaction:</span> {snapshot.summary_line_2}
                      </p>
                    </div>

                    {/* Source Link */}
                    {snapshot.source_url && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <a
                          href={snapshot.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <ExternalLink className="w-3 h-3" />
                          View original article
                        </a>
                      </div>
                    )}
                  </div>
                ))}

                {filteredAndSortedHistory.length === 0 && (
                  <div className="text-center py-12">
                    <Newspaper className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No events found</h3>
                    <p className="text-gray-600">
                      {searchQuery || categoryFilter !== 'all' || impactFilter !== 'all'
                        ? 'Try adjusting your filters to see more results.'
                        : 'No news events have been recorded for this stock yet.'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-xl font-semibold text-gray-900">Event Details</h3>
                <button
                  onClick={() => setSelectedEvent(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Category</label>
                    <div className="flex items-center gap-2 mt-1">
                      {getCategoryIcon(selectedEvent.category)}
                      <span>{formatCategory(selectedEvent.category)}</span>
                    </div>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Impact</label>
                    <div className="mt-1">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(selectedEvent.impact)}`}>
                        {selectedEvent.impact.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700">Timestamp</label>
                  <p className="mt-1 text-sm text-gray-900">
                    {new Date(selectedEvent.timestamp).toLocaleString()}
                  </p>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700">Event Summary</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedEvent.summary_line_1}</p>
                </div>

                <div>
                  <label className="text-sm font-medium text-gray-700">Market Reaction</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedEvent.summary_line_2}</p>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">1 Hour Change</label>
                    <p className={`mt-1 text-lg font-semibold ${selectedEvent.price_change_1h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {selectedEvent.price_change_1h >= 0 ? '+' : ''}{selectedEvent.price_change_1h.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">24 Hour Change</label>
                    <p className={`mt-1 text-lg font-semibold ${selectedEvent.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {selectedEvent.price_change_24h >= 0 ? '+' : ''}{selectedEvent.price_change_24h.toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Confidence</label>
                    <p className="mt-1 text-lg font-semibold text-blue-600">
                      {(selectedEvent.confidence_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>

                {selectedEvent.source_url && (
                  <div>
                    <label className="text-sm font-medium text-gray-700">Source</label>
                    <a
                      href={selectedEvent.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-1 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                    >
                      <ExternalLink className="w-4 h-4" />
                      View original article
                    </a>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewsIntelligenceDashboard;
