import React, { useState, useEffect } from 'react';
import { 
  Play, 
  Pause, 
  RefreshCw, 
  Zap, 
  Activity, 
  CheckCircle, 
  AlertCircle,
  Clock,
  TrendingUp,
  Database,
  Brain,
  Newspaper
} from 'lucide-react';
import toast from 'react-hot-toast';

interface PipelineStatus {
  available: boolean;
  processed_articles: number;
  fmp_api_configured: boolean;
  grok_api_configured: boolean;
}

interface ProcessedSnapshot {
  ticker: string;
  timestamp: string;
  category: string;
  impact: string;
  price_change_1h: number;
  price_change_24h: number;
  summary_line_1: string;
  summary_line_2: string;
  confidence_score: number;
}

const AutomatedPipelineDashboard: React.FC = () => {
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatus | null>(null);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [selectedTickers, setSelectedTickers] = useState<string[]>(['AAPL', 'TSLA', 'MSFT']);
  const [newTicker, setNewTicker] = useState('');
  const [intervalMinutes, setIntervalMinutes] = useState(30);
  const [isProcessing, setIsProcessing] = useState(false);
  const [recentSnapshots, setRecentSnapshots] = useState<ProcessedSnapshot[]>([]);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    fetchPipelineStatus();
  }, []);

  const fetchPipelineStatus = async () => {
    try {
      const response = await fetch('/api/app_supabase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'get_pipeline_status'
        })
      });

      const result = await response.json();
      if (result.success) {
        setPipelineStatus(result.pipeline_status);
      }
    } catch (error) {
      console.error('Error fetching pipeline status:', error);
    }
  };

  const triggerAnalysis = async (ticker: string) => {
    setIsProcessing(true);
    try {
      const response = await fetch('/api/app_supabase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'trigger_automated_news_analysis',
          ticker: ticker
        })
      });

      const result = await response.json();
      if (result.success) {
        setRecentSnapshots(prev => [...result.snapshots, ...prev].slice(0, 10));
        setLastUpdate(new Date());
        toast.success(`Processed ${result.snapshots_created} articles for ${ticker}`);
      } else {
        toast.error(`Failed to analyze ${ticker}: ${result.error}`);
      }
    } catch (error) {
      console.error('Error triggering analysis:', error);
      toast.error('Failed to trigger analysis');
    } finally {
      setIsProcessing(false);
    }
  };

  const startContinuousMonitoring = async () => {
    try {
      const response = await fetch('/api/app_supabase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'start_continuous_monitoring',
          tickers: selectedTickers,
          interval_minutes: intervalMinutes
        })
      });

      const result = await response.json();
      if (result.success) {
        setIsMonitoring(true);
        toast.success('Continuous monitoring started');
      } else {
        toast.error(`Failed to start monitoring: ${result.error}`);
      }
    } catch (error) {
      console.error('Error starting monitoring:', error);
      toast.error('Failed to start monitoring');
    }
  };

  const addTicker = () => {
    if (newTicker && !selectedTickers.includes(newTicker.toUpperCase())) {
      setSelectedTickers([...selectedTickers, newTicker.toUpperCase()]);
      setNewTicker('');
    }
  };

  const removeTicker = (ticker: string) => {
    setSelectedTickers(selectedTickers.filter(t => t !== ticker));
  };

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

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Zap className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Automated News Pipeline</h1>
        </div>
        <p className="text-gray-600">
          Real-time news analysis powered by Financial Modeling Prep API and Grok 4 AI
        </p>
      </div>

      {/* Pipeline Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-2">
            <Activity className={`w-5 h-5 ${pipelineStatus?.available ? 'text-green-600' : 'text-red-600'}`} />
            <h3 className="font-medium text-gray-900">Pipeline Status</h3>
          </div>
          <p className={`text-sm ${pipelineStatus?.available ? 'text-green-600' : 'text-red-600'}`}>
            {pipelineStatus?.available ? 'Active' : 'Inactive'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-2">
            <Database className="w-5 h-5 text-blue-600" />
            <h3 className="font-medium text-gray-900">Articles Processed</h3>
          </div>
          <p className="text-2xl font-bold text-blue-600">
            {pipelineStatus?.processed_articles || 0}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-2">
            <CheckCircle className={`w-5 h-5 ${pipelineStatus?.fmp_api_configured ? 'text-green-600' : 'text-red-600'}`} />
            <h3 className="font-medium text-gray-900">FMP API</h3>
          </div>
          <p className={`text-sm ${pipelineStatus?.fmp_api_configured ? 'text-green-600' : 'text-red-600'}`}>
            {pipelineStatus?.fmp_api_configured ? 'Configured' : 'Not Configured'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center gap-3 mb-2">
            <Brain className={`w-5 h-5 ${pipelineStatus?.grok_api_configured ? 'text-green-600' : 'text-red-600'}`} />
            <h3 className="font-medium text-gray-900">Grok 4 AI</h3>
          </div>
          <p className={`text-sm ${pipelineStatus?.grok_api_configured ? 'text-green-600' : 'text-red-600'}`}>
            {pipelineStatus?.grok_api_configured ? 'Configured' : 'Not Configured'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Control Panel */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Control Panel</h2>

          {/* Ticker Management */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Monitored Tickers
            </label>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={newTicker}
                onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Add ticker (e.g., AAPL)"
                onKeyPress={(e) => e.key === 'Enter' && addTicker()}
              />
              <button
                onClick={addTicker}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Add
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {selectedTickers.map(ticker => (
                <span
                  key={ticker}
                  className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  {ticker}
                  <button
                    onClick={() => removeTicker(ticker)}
                    className="text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>

          {/* Monitoring Interval */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Monitoring Interval
            </label>
            <select
              value={intervalMinutes}
              onChange={(e) => setIntervalMinutes(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={15}>15 minutes</option>
              <option value={30}>30 minutes</option>
              <option value={60}>1 hour</option>
              <option value={120}>2 hours</option>
            </select>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={startContinuousMonitoring}
              disabled={isMonitoring || selectedTickers.length === 0}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              <Play className="w-4 h-4" />
              {isMonitoring ? 'Monitoring Active' : 'Start Continuous Monitoring'}
            </button>

            <div className="grid grid-cols-2 gap-3">
              {selectedTickers.slice(0, 2).map(ticker => (
                <button
                  key={ticker}
                  onClick={() => triggerAnalysis(ticker)}
                  disabled={isProcessing}
                  className="flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  {isProcessing ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Zap className="w-4 h-4" />
                  )}
                  Analyze {ticker}
                </button>
              ))}
            </div>

            <button
              onClick={fetchPipelineStatus}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              Refresh Status
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Recent Activity</h2>
            {lastUpdate && (
              <div className="text-xs text-gray-500 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                Last update: {lastUpdate.toLocaleTimeString()}
              </div>
            )}
          </div>

          <div className="space-y-4 max-h-96 overflow-y-auto">
            {recentSnapshots.length > 0 ? (
              recentSnapshots.map((snapshot, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">{snapshot.ticker}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(snapshot.impact)}`}>
                        {snapshot.impact.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(snapshot.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  
                  <div className="space-y-1 mb-3">
                    <p className="text-sm text-gray-900">{snapshot.summary_line_1}</p>
                    <p className="text-sm text-gray-700">{snapshot.summary_line_2}</p>
                  </div>
                  
                  <div className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-4">
                      <span className={`flex items-center gap-1 ${snapshot.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        <TrendingUp className="w-3 h-3" />
                        {snapshot.price_change_24h >= 0 ? '+' : ''}{snapshot.price_change_24h.toFixed(1)}% (24h)
                      </span>
                      <span className="text-gray-500">
                        Confidence: {(snapshot.confidence_score * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8">
                <Newspaper className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Recent Activity</h3>
                <p className="text-gray-600">
                  Trigger analysis or start monitoring to see processed articles here.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8">
        <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">
          Automated News Intelligence Pipeline
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Database className="w-6 h-6 text-blue-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">1. Fetch News</h4>
            <p className="text-sm text-gray-600">
              Financial Modeling Prep API pulls latest articles for monitored stocks
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">2. Price Impact</h4>
            <p className="text-sm text-gray-600">
              Automatically tracks price changes 1h and 24h after news publication
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Brain className="w-6 h-6 text-purple-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">3. AI Analysis</h4>
            <p className="text-sm text-gray-600">
              Grok 4 analyzes and compresses articles into 2-sentence summaries
            </p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
              <Activity className="w-6 h-6 text-orange-600" />
            </div>
            <h4 className="font-medium text-gray-900 mb-2">4. Personality</h4>
            <p className="text-sm text-gray-600">
              Builds stock personality profiles based on historical news reactions
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutomatedPipelineDashboard;
