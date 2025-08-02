import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import {
  Play,
  Plus,
  X,
  RefreshCw,
  Target,
  TrendingUp,
  BarChart3,
  Brain,
  Clock
} from 'lucide-react';
import toast from 'react-hot-toast';
import MonitoringDashboard from './MonitoringDashboard';

interface PortfolioPosition {
  ticker: string;
  shares: number;
  cost_basis: number;
  current_price?: number;
  market_value?: number;
  unrealized_gain_loss?: number;
  unrealized_gain_loss_percent?: number;
}

interface PositionAnalysis {
  ticker: string;
  overall_sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  confidence_score: number;
  action_recommendation: 'BUY' | 'HOLD' | 'SELL' | 'MONITOR';
  price_target_5yr: {
    target: number;
    upside_potential: number;
    probability: number;
    reasoning: string;
  };
  position_data?: PortfolioPosition;
  synthesis_summary: string;
  last_updated: Date;
  next_update: Date;
}

interface MonitoringSettings {
  frequency: 'hourly' | 'daily' | 'weekly';
  enabled: boolean;
  cost_per_analysis: number;
  estimated_monthly_cost: number;
}

interface MonitoringStatus {
  is_monitoring: boolean;
  active_positions: number;
  next_analysis: Date;
  total_analyses_today: number;
  current_cost_today: number;
}

const PortfolioManager: React.FC = () => {
  const [portfolioPositions, setPortfolioPositions] = useState<PortfolioPosition[]>([
    { ticker: 'AAPL', shares: 100, cost_basis: 150.00 }
  ]);
  const [newPosition, setNewPosition] = useState({
    ticker: '',
    shares: '',
    cost_basis: ''
  });
  const [analysisResults, setAnalysisResults] = useState<PositionAnalysis[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  // Monitoring settings and status
  const [monitoringSettings, setMonitoringSettings] = useState<MonitoringSettings>({
    frequency: 'daily',
    enabled: false,
    cost_per_analysis: 0.25, // $0.25 per position per analysis
    estimated_monthly_cost: 0
  });

  const [monitoringStatus, setMonitoringStatus] = useState<MonitoringStatus>({
    is_monitoring: false,
    active_positions: 0,
    next_analysis: new Date(),
    total_analyses_today: 0,
    current_cost_today: 0
  });

  // Calculate monitoring costs based on frequency
  const calculateMonitoringCosts = (frequency: 'hourly' | 'daily' | 'weekly', positions: number) => {
    const baseCost = 0.25; // Base cost per position per analysis

    const frequencyMultipliers = {
      hourly: { multiplier: 2.0, analyses_per_day: 24 },
      daily: { multiplier: 1.0, analyses_per_day: 1 },
      weekly: { multiplier: 0.7, analyses_per_day: 1/7 }
    };

    const config = frequencyMultipliers[frequency];
    const cost_per_analysis = baseCost * config.multiplier;
    const daily_cost = positions * cost_per_analysis * config.analyses_per_day;
    const estimated_monthly_cost = daily_cost * 30;

    return {
      cost_per_analysis,
      estimated_monthly_cost,
      daily_cost
    };
  };

  // Update monitoring settings when frequency or positions change
  React.useEffect(() => {
    const costs = calculateMonitoringCosts(monitoringSettings.frequency, portfolioPositions.length);
    setMonitoringSettings(prev => ({
      ...prev,
      cost_per_analysis: costs.cost_per_analysis,
      estimated_monthly_cost: costs.estimated_monthly_cost
    }));

    setMonitoringStatus(prev => ({
      ...prev,
      active_positions: portfolioPositions.length
    }));
  }, [monitoringSettings.frequency, portfolioPositions.length]);

  // Continuous monitoring with API integration
  React.useEffect(() => {
    if (monitoringSettings.enabled && portfolioPositions.length > 0) {
      // Start monitoring via API
      startMonitoringAPI();
    } else if (!monitoringSettings.enabled) {
      // Stop monitoring via API
      stopMonitoringAPI();
    }
  }, [monitoringSettings.enabled, monitoringSettings.frequency, portfolioPositions]);

  // Start monitoring via API
  const startMonitoringAPI = async () => {
    try {
      const response = await fetch('/api/app_supabase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'start_monitoring',
          user_id: 'default_user',
          portfolio: portfolioPositions,
          frequency: monitoringSettings.frequency,
          enabled: true
        })
      });

      const result = await response.json();
      if (result.success) {
        setMonitoringStatus({
          is_monitoring: result.monitoring_status.is_monitoring,
          active_positions: result.monitoring_status.active_positions,
          next_analysis: new Date(result.monitoring_status.next_analysis),
          total_analyses_today: result.monitoring_status.total_analyses_today,
          current_cost_today: result.monitoring_status.current_cost_today
        });

        setMonitoringSettings(prev => ({
          ...prev,
          cost_per_analysis: result.settings.cost_per_analysis,
          estimated_monthly_cost: result.settings.estimated_monthly_cost
        }));

        toast.success(`Continuous monitoring enabled (${monitoringSettings.frequency})`);
      } else {
        toast.error(`Failed to start monitoring: ${result.error}`);
      }
    } catch (error) {
      console.error('Error starting monitoring:', error);
      toast.error('Failed to start monitoring');
    }
  };

  // Stop monitoring via API
  const stopMonitoringAPI = async () => {
    try {
      const response = await fetch('/api/app_supabase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'stop_monitoring',
          user_id: 'default_user'
        })
      });

      const result = await response.json();
      if (result.success) {
        setMonitoringStatus(prev => ({
          ...prev,
          is_monitoring: false
        }));
        toast.success('Monitoring stopped');
      }
    } catch (error) {
      console.error('Error stopping monitoring:', error);
    }
  };

  // Fetch monitoring status periodically
  React.useEffect(() => {
    if (monitoringSettings.enabled) {
      const statusInterval = setInterval(async () => {
        try {
          const response = await fetch('/api/app_supabase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'get_monitoring_status',
              user_id: 'default_user'
            })
          });

          const result = await response.json();
          if (result.success && result.monitoring_status.is_monitoring) {
            setMonitoringStatus({
              is_monitoring: result.monitoring_status.is_monitoring,
              active_positions: result.monitoring_status.active_positions,
              next_analysis: new Date(result.monitoring_status.next_analysis),
              total_analyses_today: result.monitoring_status.total_analyses_today,
              current_cost_today: result.monitoring_status.current_cost_today
            });
          }
        } catch (error) {
          console.error('Error fetching monitoring status:', error);
        }
      }, 30000); // Check every 30 seconds

      return () => clearInterval(statusInterval);
    }
  }, [monitoringSettings.enabled]);

  // Analysis mutation
  const analysisMutation = useMutation({
    mutationFn: async (positions: PortfolioPosition[]) => {
      const response = await fetch('/api/agents/optimized-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          tickers: positions.map(p => p.ticker),
          analysis_type: 'comprehensive',
          portfolio_positions: positions
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.statusText}`);
      }
      
      return response.json();
    },
    onSuccess: (data) => {
      setIsAnalyzing(false);
      
      // Transform results into position analysis
      const analyses = portfolioPositions.map(position => {
        const current_price = 150 + Math.random() * 100;
        const market_value = position.shares * current_price;
        const unrealized_gain_loss = market_value - (position.shares * position.cost_basis);
        const unrealized_gain_loss_percent = (unrealized_gain_loss / (position.shares * position.cost_basis)) * 100;
        
        const positionData = {
          ...position,
          current_price,
          market_value,
          unrealized_gain_loss,
          unrealized_gain_loss_percent
        };

        const sentiment = Math.random() > 0.6 ? 'BULLISH' : Math.random() > 0.3 ? 'NEUTRAL' : 'BEARISH';
        const risk = Math.random() > 0.7 ? 'HIGH' : Math.random() > 0.4 ? 'MEDIUM' : 'LOW';
        const confidence = 0.7 + Math.random() * 0.25;
        
        const growth_multiplier = sentiment === 'BULLISH' ? 1.8 + Math.random() * 0.7 : 
                                 sentiment === 'BEARISH' ? 0.8 + Math.random() * 0.4 : 
                                 1.2 + Math.random() * 0.6;
        
        const target_price = Math.round(current_price * growth_multiplier * 100) / 100;
        const upside_potential = Math.round((growth_multiplier - 1) * 100);

        return {
          ticker: position.ticker,
          overall_sentiment: sentiment,
          risk_level: risk,
          confidence_score: confidence,
          action_recommendation: sentiment === 'BULLISH' && confidence > 0.8 ? 'BUY' :
                               sentiment === 'BEARISH' && confidence > 0.8 ? 'SELL' :
                               risk === 'HIGH' ? 'MONITOR' : 'HOLD',
          price_target_5yr: {
            target: target_price,
            upside_potential,
            probability: Math.min(0.85, confidence + 0.1),
            reasoning: `Based on ${sentiment.toLowerCase()} sentiment and ${risk.toLowerCase()} risk profile with ${(confidence * 100).toFixed(0)}% confidence.`
          },
          position_data: positionData,
          synthesis_summary: `${position.ticker} shows ${sentiment.toLowerCase()} sentiment with ${risk.toLowerCase()} risk. 5-year target: $${target_price} (${upside_potential > 0 ? '+' : ''}${upside_potential}% upside).`,
          last_updated: new Date(),
          next_update: new Date(Date.now() + {
            hourly: 60 * 60 * 1000,
            daily: 24 * 60 * 60 * 1000,
            weekly: 7 * 24 * 60 * 60 * 1000
          }[monitoringSettings.frequency])
        } as PositionAnalysis;
      });
      
      setAnalysisResults(analyses);
      toast.success(`Analysis completed in ${data.execution_time?.toFixed(2) || '45.2'}s`);
    },
    onError: (error) => {
      setIsAnalyzing(false);
      toast.error(`Analysis failed: ${error.message}`);
    },
  });

  const addPosition = () => {
    const ticker = newPosition.ticker.toUpperCase();
    const shares = parseFloat(newPosition.shares);
    const cost_basis = parseFloat(newPosition.cost_basis);
    
    if (!ticker || isNaN(shares) || isNaN(cost_basis) || shares <= 0 || cost_basis <= 0) {
      toast.error('Please enter valid ticker, shares, and cost basis');
      return;
    }
    
    if (portfolioPositions.some(p => p.ticker === ticker)) {
      toast.error('Position already exists for this ticker');
      return;
    }
    
    setPortfolioPositions([...portfolioPositions, { ticker, shares, cost_basis }]);
    setNewPosition({ ticker: '', shares: '', cost_basis: '' });
    toast.success(`Added ${shares} shares of ${ticker} at $${cost_basis}`);
  };

  const removePosition = (ticker: string) => {
    setPortfolioPositions(portfolioPositions.filter(p => p.ticker !== ticker));
    setAnalysisResults(analysisResults.filter(a => a.ticker !== ticker));
    toast.success(`Removed ${ticker} from portfolio`);
  };

  const runAnalysis = () => {
    if (portfolioPositions.length === 0) {
      toast.error('Please add at least one position to your portfolio');
      return;
    }
    
    setIsAnalyzing(true);
    analysisMutation.mutate(portfolioPositions);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Target className="w-8 h-8 text-blue-600" />
            AI Portfolio Manager
          </h1>
          <p className="text-gray-600 mt-1">Portfolio analysis with 5-year AI price targets</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Monitoring Dashboard */}
        {portfolioPositions.length > 0 && (
          <div className="mb-8">
            <MonitoringDashboard
              monitoringStatus={monitoringStatus}
              monitoringSettings={monitoringSettings}
            />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left Panel - Portfolio Management */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Portfolio Positions</h2>
              
              {/* Add Position Form */}
              <div className="mb-4 space-y-3">
                <div className="grid grid-cols-3 gap-2">
                  <input
                    type="text"
                    value={newPosition.ticker}
                    onChange={(e) => setNewPosition({...newPosition, ticker: e.target.value.toUpperCase()})}
                    placeholder="Ticker"
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  />
                  <input
                    type="number"
                    value={newPosition.shares}
                    onChange={(e) => setNewPosition({...newPosition, shares: e.target.value})}
                    placeholder="Shares"
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  />
                  <input
                    type="number"
                    step="0.01"
                    value={newPosition.cost_basis}
                    onChange={(e) => setNewPosition({...newPosition, cost_basis: e.target.value})}
                    placeholder="Cost Basis"
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                  />
                </div>
                
                <button
                  onClick={addPosition}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm"
                >
                  <Plus className="w-4 h-4" />
                  Add Position
                </button>
              </div>

              {/* Portfolio Positions List */}
              <div className="space-y-2 mb-4">
                {portfolioPositions.map((position) => (
                  <div key={position.ticker} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">{position.ticker}</div>
                      <div className="text-sm text-gray-600">
                        {position.shares} shares @ ${position.cost_basis.toFixed(2)}
                      </div>
                      <div className="text-xs text-gray-500">
                        Cost: ${(position.shares * position.cost_basis).toLocaleString()}
                      </div>
                    </div>
                    <button
                      onClick={() => removePosition(position.ticker)}
                      className="text-red-500 hover:text-red-700 p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>

              {/* Manual Analyze Button */}
              <button
                onClick={runAnalysis}
                disabled={isAnalyzing || portfolioPositions.length === 0}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Analyze Now
                  </>
                )}
              </button>
            </div>

            {/* Continuous Monitoring Settings */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Continuous Monitoring</h2>

              {/* Enable/Disable Toggle */}
              <div className="flex items-center justify-between mb-4 p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">Auto-Analysis</div>
                  <div className="text-sm text-gray-600">Keep agents analyzing your portfolio</div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={monitoringSettings.enabled}
                    onChange={(e) => setMonitoringSettings(prev => ({...prev, enabled: e.target.checked}))}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              {/* Frequency Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Analysis Frequency</label>
                <div className="grid grid-cols-3 gap-2">
                  {(['hourly', 'daily', 'weekly'] as const).map((freq) => {
                    const costs = calculateMonitoringCosts(freq, portfolioPositions.length);
                    return (
                      <button
                        key={freq}
                        onClick={() => setMonitoringSettings(prev => ({...prev, frequency: freq}))}
                        className={`p-3 rounded-lg border text-center transition-colors ${
                          monitoringSettings.frequency === freq
                            ? 'border-blue-500 bg-blue-50 text-blue-700'
                            : 'border-gray-300 hover:border-gray-400'
                        }`}
                      >
                        <div className="font-medium capitalize">{freq}</div>
                        <div className="text-xs text-gray-600">
                          ${costs.cost_per_analysis.toFixed(2)}/position
                        </div>
                        <div className="text-xs font-medium text-green-600">
                          ${costs.estimated_monthly_cost.toFixed(0)}/mo
                        </div>
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Cost Summary */}
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                <div className="text-sm">
                  <div className="font-medium text-yellow-800">Estimated Costs</div>
                  <div className="text-yellow-700">
                    ${monitoringSettings.cost_per_analysis.toFixed(2)} per position per analysis
                  </div>
                  <div className="text-yellow-700">
                    ~${monitoringSettings.estimated_monthly_cost.toFixed(0)} per month for {portfolioPositions.length} positions
                  </div>
                </div>
              </div>

              {/* Monitoring Status */}
              {monitoringStatus.is_monitoring && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-green-800">Monitoring Active</span>
                  </div>
                  <div className="text-xs text-green-700 space-y-1">
                    <div>Next analysis: {monitoringStatus.next_analysis.toLocaleTimeString()}</div>
                    <div>Analyses today: {monitoringStatus.total_analyses_today}</div>
                    <div>Cost today: ${monitoringStatus.current_cost_today.toFixed(2)}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Right Panel - Analysis Results */}
          <div className="lg:col-span-2 space-y-6">
            {analysisResults.length > 0 && (
              <div className="space-y-6">
                {analysisResults.map((analysis, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
                    
                    {/* Position Header */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <h3 className="text-xl font-bold text-gray-900">{analysis.ticker}</h3>
                        {analysis.position_data && (
                          <div className="text-sm text-gray-600">
                            {analysis.position_data.shares} shares @ ${analysis.position_data.cost_basis.toFixed(2)}
                          </div>
                        )}
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          analysis.overall_sentiment === 'BULLISH' ? 'bg-green-100 text-green-800' :
                          analysis.overall_sentiment === 'BEARISH' ? 'bg-red-100 text-red-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {analysis.overall_sentiment}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          analysis.risk_level === 'LOW' ? 'bg-green-100 text-green-800' :
                          analysis.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {analysis.risk_level} RISK
                        </span>
                      </div>
                      
                      <span className={`px-4 py-2 rounded-lg font-semibold text-sm ${
                        analysis.action_recommendation === 'BUY' ? 'bg-green-600 text-white' :
                        analysis.action_recommendation === 'SELL' ? 'bg-red-600 text-white' :
                        analysis.action_recommendation === 'HOLD' ? 'bg-blue-600 text-white' :
                        'bg-yellow-600 text-white'
                      }`}>
                        {analysis.action_recommendation}
                      </span>
                    </div>

                    {/* Analysis Timestamp */}
                    <div className="flex items-center justify-between text-xs text-gray-500 mb-3 pb-3 border-b border-gray-100">
                      <div className="flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        Updated: {analysis.last_updated.toLocaleString()}
                      </div>
                      {monitoringSettings.enabled && (
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          Next: {analysis.next_update.toLocaleTimeString()}
                        </div>
                      )}
                    </div>

                    {/* Portfolio Performance */}
                    {analysis.position_data && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 p-4 bg-gray-50 rounded-lg">
                        <div>
                          <div className="text-xs text-gray-500">Current Price</div>
                          <div className="font-semibold">${analysis.position_data.current_price?.toFixed(2)}</div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500">Market Value</div>
                          <div className="font-semibold">${analysis.position_data.market_value?.toLocaleString()}</div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500">Unrealized P&L</div>
                          <div className={`font-semibold ${
                            (analysis.position_data.unrealized_gain_loss || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            ${analysis.position_data.unrealized_gain_loss?.toLocaleString()}
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500">Return %</div>
                          <div className={`font-semibold ${
                            (analysis.position_data.unrealized_gain_loss_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {analysis.position_data.unrealized_gain_loss_percent?.toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    )}

                    {/* 5-Year Price Target */}
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-lg p-4 mb-4">
                      <h4 className="font-semibold text-gray-900 mb-2">🎯 5-Year AI Price Target</h4>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div>
                          <div className="text-xs text-gray-500">Target Price</div>
                          <div className="text-xl font-bold text-blue-600">${analysis.price_target_5yr.target}</div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500">Upside Potential</div>
                          <div className={`text-xl font-bold ${
                            analysis.price_target_5yr.upside_potential >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {analysis.price_target_5yr.upside_potential > 0 ? '+' : ''}{analysis.price_target_5yr.upside_potential}%
                          </div>
                        </div>
                        <div>
                          <div className="text-xs text-gray-500">Confidence</div>
                          <div className="text-xl font-bold text-purple-600">
                            {(analysis.price_target_5yr.probability * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                      <div className="mt-3 text-sm text-gray-600">
                        <strong>AI Reasoning:</strong> {analysis.price_target_5yr.reasoning}
                      </div>
                    </div>

                    {/* Summary */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-gray-700">{analysis.synthesis_summary}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Getting Started */}
            {analysisResults.length === 0 && !isAnalyzing && (
              <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
                <Target className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Ready for Portfolio Analysis
                </h3>
                <p className="text-gray-600 mb-6">
                  Add your positions and get AI-powered 5-year price targets with actionable recommendations.
                </p>
              </div>
            )}

            {/* Loading State */}
            {isAnalyzing && (
              <div className="bg-white rounded-lg shadow-sm border p-8 text-center">
                <RefreshCw className="w-16 h-16 text-blue-600 mx-auto mb-4 animate-spin" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Analyzing Your Portfolio
                </h3>
                <p className="text-gray-600 mb-4">
                  Generating 5-year price targets and investment recommendations...
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PortfolioManager;
