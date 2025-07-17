import React, { useState } from 'react';
import { Bell, RefreshCw, Settings, User, AlertCircle } from 'lucide-react';
import { useSystemStatus } from '@/hooks/useApi';
import { formatDate } from '@/utils/api';

export const Header: React.FC = () => {
  const { data: systemStatus, isLoading, refetch } = useSystemStatus();
  const [showNotifications, setShowNotifications] = useState(false);

  const handleRefresh = () => {
    refetch();
  };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left side - Current page info */}
        <div className="flex items-center space-x-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              🚀 Multi-Agent Portfolio Analysis
            </h2>
            <p className="text-sm text-gray-500">
              Real-time market analysis with AI-powered insights
            </p>
          </div>
        </div>

        {/* Right side - Status and actions */}
        <div className="flex items-center space-x-4">
          {/* System status indicator */}
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">
                {isLoading ? 'Checking...' : 'System Online'}
              </span>
            </div>
            {systemStatus?.success && (
              <div className="text-xs text-gray-500">
                {systemStatus.data?.portfolio?.length || 0} stocks tracked
              </div>
            )}
          </div>

          {/* Refresh button */}
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50 transition-colors"
            title="Refresh system status"
          >
            <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
          </button>

          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50 transition-colors relative"
            >
              <Bell className="w-5 h-5" />
              {/* Notification badge */}
              <span className="absolute -top-1 -right-1 w-3 h-3 bg-error-500 rounded-full text-xs text-white flex items-center justify-center">
                3
              </span>
            </button>

            {/* Notifications dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                <div className="p-4 border-b border-gray-200">
                  <h3 className="font-medium text-gray-900">Notifications</h3>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  <div className="p-3 border-b border-gray-100 hover:bg-gray-50">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className="w-5 h-5 text-warning-500 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          High volatility detected
                        </p>
                        <p className="text-xs text-gray-500">
                          TSLA showing 8.5% volatility - 5 minutes ago
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 border-b border-gray-100 hover:bg-gray-50">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className="w-5 h-5 text-success-500 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          Analysis completed
                        </p>
                        <p className="text-xs text-gray-500">
                          Portfolio analysis finished - 10 minutes ago
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="p-3 hover:bg-gray-50">
                    <div className="flex items-start space-x-3">
                      <AlertCircle className="w-5 h-5 text-primary-500 mt-0.5" />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          New insights available
                        </p>
                        <p className="text-xs text-gray-500">
                          3 new insights from knowledge evolution - 15 minutes ago
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="p-3 border-t border-gray-200">
                  <button className="text-sm text-primary-600 hover:text-primary-700">
                    View all notifications
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* User menu */}
          <div className="relative">
            <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50 transition-colors">
              <User className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}; 