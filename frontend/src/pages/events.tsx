import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/layout/Layout';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { useEvents } from '@/hooks/useApi';
import { formatDate } from '@/utils/api';
import { 
  Bell, 
  AlertTriangle, 
  CheckCircle, 
  Info,
  XCircle,
  RefreshCw,
  Trash2,
  Play,
  Pause,
  Filter,
  Calendar,
  TrendingUp,
  Clock
} from 'lucide-react';

const EventMonitoring: React.FC = () => {
  const { events, isAutoRefresh, addEvent, clearEvents, toggleAutoRefresh } = useEvents();
  const [filter, setFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  // Simulate real-time events
  useEffect(() => {
    const simulateEvents = () => {
      const eventTypes = ['INFO', 'SUCCESS', 'WARNING', 'ERROR'] as const;
      const tickers = ['AAPL', 'GOOGL', 'TSLA', 'AMZN', 'MSFT', 'SYSTEM'];
      const messages = [
        'Portfolio analysis completed successfully',
        'High volatility detected in trading session',
        'Email notification sent to administrators',
        'Market correlation analysis updated',
        'Risk assessment threshold exceeded',
        'Knowledge evolution pattern identified',
        'Background scheduler executed analysis',
        'API connection established successfully',
        'Database sync completed',
        'New insights generated from analysis'
      ];

      const randomEvent = {
        type: eventTypes[Math.floor(Math.random() * eventTypes.length)],
        ticker: tickers[Math.floor(Math.random() * tickers.length)],
        message: messages[Math.floor(Math.random() * messages.length)]
      };

      addEvent(randomEvent);
    };

    if (isAutoRefresh) {
      const interval = setInterval(simulateEvents, 3000);
      return () => clearInterval(interval);
    }
  }, [isAutoRefresh, addEvent]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'SUCCESS':
        return <CheckCircle className="w-5 h-5 text-success-600" />;
      case 'WARNING':
        return <AlertTriangle className="w-5 h-5 text-warning-600" />;
      case 'ERROR':
        return <XCircle className="w-5 h-5 text-error-600" />;
      default:
        return <Info className="w-5 h-5 text-primary-600" />;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case 'SUCCESS':
        return 'bg-success-50 border-success-200';
      case 'WARNING':
        return 'bg-warning-50 border-warning-200';
      case 'ERROR':
        return 'bg-error-50 border-error-200';
      default:
        return 'bg-primary-50 border-primary-200';
    }
  };

  const filteredEvents = events.filter(event => {
    const matchesFilter = filter === 'all' || event.type.toLowerCase() === filter.toLowerCase();
    const matchesSearch = event.ticker.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         event.message.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const eventCounts = {
    all: events.length,
    success: events.filter(e => e.type === 'SUCCESS').length,
    warning: events.filter(e => e.type === 'WARNING').length,
    error: events.filter(e => e.type === 'ERROR').length,
    info: events.filter(e => e.type === 'INFO').length
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Event Monitoring</h1>
            <p className="text-gray-600">Real-time system events and alerts</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={toggleAutoRefresh}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                isAutoRefresh
                  ? 'bg-success-600 text-white hover:bg-success-700'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {isAutoRefresh ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
              <span>{isAutoRefresh ? 'Stop' : 'Start'} Auto-refresh</span>
            </button>
            <button
              onClick={clearEvents}
              className="flex items-center space-x-2 px-4 py-2 bg-error-600 text-white rounded-lg hover:bg-error-700"
            >
              <Trash2 className="w-4 h-4" />
              <span>Clear Events</span>
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Events</p>
                <p className="text-2xl font-bold text-gray-900">{eventCounts.all}</p>
              </div>
              <Bell className="w-8 h-8 text-primary-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Success</p>
                <p className="text-2xl font-bold text-success-600">{eventCounts.success}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-success-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Warnings</p>
                <p className="text-2xl font-bold text-warning-600">{eventCounts.warning}</p>
              </div>
              <AlertTriangle className="w-8 h-8 text-warning-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Errors</p>
                <p className="text-2xl font-bold text-error-600">{eventCounts.error}</p>
              </div>
              <XCircle className="w-8 h-8 text-error-600" />
            </div>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Info</p>
                <p className="text-2xl font-bold text-primary-600">{eventCounts.info}</p>
              </div>
              <Info className="w-8 h-8 text-primary-600" />
            </div>
          </div>
        </div>

        {/* Filters and Search */}
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <div className="flex items-center justify-between space-x-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="w-5 h-5 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Filter:</span>
              </div>
              <div className="flex space-x-2">
                {[
                  { key: 'all', label: 'All', count: eventCounts.all },
                  { key: 'success', label: 'Success', count: eventCounts.success },
                  { key: 'warning', label: 'Warning', count: eventCounts.warning },
                  { key: 'error', label: 'Error', count: eventCounts.error },
                  { key: 'info', label: 'Info', count: eventCounts.info }
                ].map(({ key, label, count }) => (
                  <button
                    key={key}
                    onClick={() => setFilter(key)}
                    className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
                      filter === key
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {label} ({count})
                  </button>
                ))}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                placeholder="Search events..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {/* Auto-refresh status */}
        {isAutoRefresh && (
          <div className="bg-success-50 border border-success-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <RefreshCw className="w-4 h-4 text-success-600 animate-spin" />
              <span className="text-sm text-success-800">Auto-refresh active - New events will appear automatically</span>
            </div>
          </div>
        )}

        {/* Events List */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Recent Events</h3>
            <p className="text-sm text-gray-500">
              Showing {filteredEvents.length} of {events.length} events
            </p>
          </div>
          
          {filteredEvents.length === 0 ? (
            <div className="p-8 text-center">
              <Bell className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-4 text-lg font-medium text-gray-900">No events found</h3>
              <p className="mt-2 text-sm text-gray-500">
                {events.length === 0
                  ? 'No events have been recorded yet. Enable auto-refresh to see real-time events.'
                  : 'No events match your current filter criteria.'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
              {filteredEvents.map((event) => (
                <div key={event.id} className={`p-4 border-l-4 ${getEventColor(event.type)}`}>
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {getEventIcon(event.type)}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900">{event.ticker}</span>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            event.type === 'SUCCESS' ? 'bg-success-100 text-success-800' :
                            event.type === 'WARNING' ? 'bg-warning-100 text-warning-800' :
                            event.type === 'ERROR' ? 'bg-error-100 text-error-800' :
                            'bg-primary-100 text-primary-800'
                          }`}>
                            {event.type}
                          </span>
                        </div>
                        <div className="flex items-center space-x-1 text-sm text-gray-500">
                          <Clock className="w-4 h-4" />
                          <span>{formatDate(event.timestamp)}</span>
                        </div>
                      </div>
                      <p className="mt-1 text-sm text-gray-700">{event.message}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-indigo-900 mb-2">Event Monitoring Features</h3>
          <ul className="text-sm text-indigo-800 space-y-1">
            <li>• Real-time event tracking with auto-refresh functionality</li>
            <li>• Filter events by type (Success, Warning, Error, Info)</li>
            <li>• Search through events by ticker or message content</li>
            <li>• Events are automatically categorized and color-coded</li>
            <li>• Historical event tracking with timestamps</li>
            <li>• Clear all events to start fresh monitoring</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
};

export default EventMonitoring; 