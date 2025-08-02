import React from 'react';
import { Activity, Clock, DollarSign, TrendingUp, AlertCircle } from 'lucide-react';

interface MonitoringDashboardProps {
  monitoringStatus: {
    is_monitoring: boolean;
    active_positions: number;
    next_analysis: Date;
    total_analyses_today: number;
    current_cost_today: number;
  };
  monitoringSettings: {
    frequency: 'hourly' | 'daily' | 'weekly';
    enabled: boolean;
    cost_per_analysis: number;
    estimated_monthly_cost: number;
  };
}

const MonitoringDashboard: React.FC<MonitoringDashboardProps> = ({
  monitoringStatus,
  monitoringSettings
}) => {
  const getFrequencyColor = (frequency: string) => {
    switch (frequency) {
      case 'hourly': return 'text-red-600 bg-red-50';
      case 'daily': return 'text-blue-600 bg-blue-50';
      case 'weekly': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTimeUntilNext = () => {
    const now = new Date();
    const diff = monitoringStatus.next_analysis.getTime() - now.getTime();
    
    if (diff <= 0) return 'Analyzing now...';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  };

  if (!monitoringSettings.enabled) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <div className="flex items-center gap-2 text-gray-600">
          <Activity className="w-4 h-4" />
          <span className="text-sm">Continuous monitoring is disabled</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
          <h3 className="font-medium text-gray-900">Live Monitoring</h3>
        </div>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getFrequencyColor(monitoringSettings.frequency)}`}>
          {monitoringSettings.frequency.toUpperCase()}
        </span>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Positions */}
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">{monitoringStatus.active_positions}</div>
          <div className="text-xs text-gray-600">Active Positions</div>
        </div>

        {/* Next Analysis */}
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">{getTimeUntilNext()}</div>
          <div className="text-xs text-gray-600">Next Analysis</div>
        </div>

        {/* Today's Analyses */}
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">{monitoringStatus.total_analyses_today}</div>
          <div className="text-xs text-gray-600">Analyses Today</div>
        </div>

        {/* Today's Cost */}
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600">${monitoringStatus.current_cost_today.toFixed(2)}</div>
          <div className="text-xs text-gray-600">Cost Today</div>
        </div>
      </div>

      {/* Cost Warning */}
      {monitoringSettings.frequency === 'hourly' && (
        <div className="flex items-start gap-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <AlertCircle className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
          <div className="text-sm">
            <div className="font-medium text-yellow-800">High Frequency Monitoring</div>
            <div className="text-yellow-700">
              Hourly analysis provides real-time insights but increases costs significantly.
              Estimated: ${monitoringSettings.estimated_monthly_cost.toFixed(0)}/month
            </div>
          </div>
        </div>
      )}

      {/* Next Analysis Details */}
      <div className="flex items-center justify-between text-sm text-gray-600 pt-2 border-t border-gray-100">
        <div className="flex items-center gap-1">
          <Clock className="w-3 h-3" />
          Next analysis: {monitoringStatus.next_analysis.toLocaleTimeString()}
        </div>
        <div className="flex items-center gap-1">
          <DollarSign className="w-3 h-3" />
          ${monitoringSettings.cost_per_analysis.toFixed(2)} per position
        </div>
      </div>
    </div>
  );
};

export default MonitoringDashboard;
