import React, { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { MetricCard } from '@/components/common/MetricCard';
import { useScheduler } from '@/hooks/useApi';
import { formatDate } from '@/utils/api';
import { 
  Clock, 
  Play, 
  Pause, 
  Settings,
  Calendar,
  Activity,
  AlertCircle,
  CheckCircle,
  Timer,
  RefreshCw,
  Zap
} from 'lucide-react';

const BackgroundScheduling: React.FC = () => {
  const { isRunning, interval, lastRun, nextRun, startScheduler, stopScheduler, updateInterval } = useScheduler();
  const [newInterval, setNewInterval] = useState(interval);
  const [selectedPreset, setSelectedPreset] = useState<number | null>(null);

  const intervalPresets = [
    { value: 300, label: '5 minutes', description: 'High frequency monitoring' },
    { value: 900, label: '15 minutes', description: 'Active trading hours' },
    { value: 1800, label: '30 minutes', description: 'Regular monitoring' },
    { value: 3600, label: '1 hour', description: 'Standard analysis' },
    { value: 7200, label: '2 hours', description: 'Extended intervals' },
    { value: 14400, label: '4 hours', description: 'Daily market checks' },
    { value: 21600, label: '6 hours', description: 'Periodic updates' },
    { value: 43200, label: '12 hours', description: 'Twice daily' },
    { value: 86400, label: '24 hours', description: 'Daily analysis' }
  ];

  const handleIntervalChange = (value: number) => {
    setNewInterval(value);
    setSelectedPreset(value);
    updateInterval(value);
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  const getStatusColor = (running: boolean) => {
    return running ? 'text-success-600' : 'text-gray-600';
  };

  const getStatusIcon = (running: boolean) => {
    return running ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />;
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Background Scheduling</h1>
            <p className="text-gray-600">Configure automated portfolio analysis intervals</p>
          </div>
          <div className="flex items-center space-x-3">
            {isRunning ? (
              <button
                onClick={stopScheduler}
                className="flex items-center space-x-2 px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700"
              >
                <Pause className="w-4 h-4" />
                <span>Stop Scheduler</span>
              </button>
            ) : (
              <button
                onClick={startScheduler}
                className="flex items-center space-x-2 px-4 py-2 bg-success-600 text-white rounded-lg hover:bg-success-700"
              >
                <Play className="w-4 h-4" />
                <span>Start Scheduler</span>
              </button>
            )}
          </div>
        </div>

        {/* Status Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <MetricCard
            title="Status"
            value={isRunning ? 'Running' : 'Stopped'}
            icon={isRunning ? CheckCircle : AlertCircle}
            subtitle="Current scheduler state"
            changeType={isRunning ? 'positive' : 'neutral'}
          />
          <MetricCard
            title="Interval"
            value={formatDuration(interval)}
            icon={Clock}
            subtitle="Analysis frequency"
          />
          <MetricCard
            title="Last Run"
            value={lastRun ? formatDate(lastRun) : 'Never'}
            icon={Calendar}
            subtitle="Previous execution"
          />
          <MetricCard
            title="Next Run"
            value={nextRun ? formatDate(nextRun) : 'Not scheduled'}
            icon={Timer}
            subtitle="Upcoming execution"
          />
        </div>

        {/* Current Status */}
        <div className={`rounded-lg border p-6 ${
          isRunning ? 'bg-success-50 border-success-200' : 'bg-gray-50 border-gray-200'
        }`}>
          <div className="flex items-center space-x-3">
            <div className={getStatusColor(isRunning)}>
              {getStatusIcon(isRunning)}
            </div>
            <div>
              <h3 className="text-lg font-medium text-gray-900">
                Scheduler {isRunning ? 'Active' : 'Inactive'}
              </h3>
              <p className="text-sm text-gray-600">
                {isRunning 
                  ? `Automatically analyzing portfolio every ${formatDuration(interval)}`
                  : 'Click "Start Scheduler" to begin automated analysis'
                }
              </p>
            </div>
          </div>
        </div>

        {/* Interval Configuration */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center space-x-2 mb-6">
            <Settings className="w-5 h-5 text-gray-600" />
            <h3 className="text-lg font-medium text-gray-900">Interval Configuration</h3>
          </div>

          <div className="space-y-6">
            {/* Preset Intervals */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Select Preset Interval
              </label>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {intervalPresets.map((preset) => (
                  <button
                    key={preset.value}
                    onClick={() => handleIntervalChange(preset.value)}
                    className={`p-4 text-left border rounded-lg transition-colors ${
                      selectedPreset === preset.value
                        ? 'border-primary-300 bg-primary-50'
                        : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">{preset.label}</span>
                      <Clock className="w-4 h-4 text-gray-600" />
                    </div>
                    <p className="text-xs text-gray-500">{preset.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Custom Interval */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Custom Interval (seconds)
              </label>
              <div className="flex items-center space-x-3">
                <input
                  type="number"
                  min="60"
                  max="86400"
                  value={newInterval}
                  onChange={(e) => setNewInterval(parseInt(e.target.value) || 3600)}
                  className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
                <span className="text-sm text-gray-500">
                  ({formatDuration(newInterval)})
                </span>
                <button
                  onClick={() => handleIntervalChange(newInterval)}
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  Update
                </button>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Minimum: 60 seconds, Maximum: 86400 seconds (24 hours)
              </p>
            </div>
          </div>
        </div>

        {/* Scheduler Features */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Scheduler Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <RefreshCw className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Automated Analysis</h4>
                  <p className="text-xs text-gray-500">
                    Automatically analyzes entire portfolio at specified intervals
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Zap className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Real-time Updates</h4>
                  <p className="text-xs text-gray-500">
                    Updates insights and risk assessments continuously
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-yellow-600" />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Alert Generation</h4>
                  <p className="text-xs text-gray-500">
                    Generates alerts for high-impact events automatically
                  </p>
                </div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Activity className="w-5 h-5 text-purple-600" />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Performance Tracking</h4>
                  <p className="text-xs text-gray-500">
                    Tracks scheduler performance and execution history
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <Settings className="w-5 h-5 text-indigo-600" />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Flexible Configuration</h4>
                  <p className="text-xs text-gray-500">
                    Configure intervals from minutes to hours based on needs
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-red-100 rounded-lg">
                  <CheckCircle className="w-5 h-5 text-red-600" />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Reliable Execution</h4>
                  <p className="text-xs text-gray-500">
                    Ensures consistent analysis execution and error handling
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Usage Recommendations */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-blue-900 mb-4">Recommended Usage</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
            <div>
              <h4 className="font-medium mb-2">Active Trading (9 AM - 4 PM)</h4>
              <ul className="space-y-1">
                <li>• 5-15 minute intervals for high-frequency monitoring</li>
                <li>• Real-time detection of market volatility</li>
                <li>• Immediate alerts for significant events</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-2">After Hours & Weekends</h4>
              <ul className="space-y-1">
                <li>• 1-4 hour intervals for general monitoring</li>
                <li>• Track overnight developments</li>
                <li>• Prepare for next trading session</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default BackgroundScheduling; 