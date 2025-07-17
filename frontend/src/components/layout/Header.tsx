import React, { useState } from 'react';
import { Bell, RefreshCw, User, AlertCircle } from 'lucide-react';
import { useSystemStatus } from '@/hooks/useApi';

export const Header: React.FC = () => {
  const { data: systemStatus, isLoading, refetch } = useSystemStatus();
  const [showNotifications, setShowNotifications] = useState(false);

  const handleRefresh = () => {
    refetch();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      case 'warning':
        return 'text-yellow-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      case 'warning':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      default:
        return <div className="w-2 h-2 bg-gray-500 rounded-full" />;
    }
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and System Status */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">PA</span>
              </div>
              <span className="text-xl font-semibold text-gray-900">Portfolio Analysis</span>
            </div>
            
            {/* System Status */}
            <div className="flex items-center space-x-2 ml-8">
              {getStatusIcon(systemStatus?.status || 'unknown')}
              <span className={`text-sm ${getStatusColor(systemStatus?.status || 'unknown')}`}>
                {systemStatus?.status === 'active' ? 'System Online' : 
                 systemStatus?.status === 'error' ? 'System Error' : 
                 systemStatus?.status === 'warning' ? 'System Warning' : 'System Status Unknown'}
              </span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={isLoading}
              className="p-2 text-gray-600 hover:text-gray-900 transition-colors disabled:opacity-50"
              title="Refresh System Status"
            >
              <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
            </button>

            {/* Notifications */}
            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 text-gray-600 hover:text-gray-900 transition-colors relative"
                title="Notifications"
              >
                <Bell className="w-5 h-5" />
                {systemStatus?.notifications && systemStatus.notifications > 0 && (
                  <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                    {systemStatus.notifications}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="p-4 border-b border-gray-200">
                    <h3 className="text-sm font-medium text-gray-900">Notifications</h3>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    {systemStatus?.recent_alerts && systemStatus.recent_alerts.length > 0 ? (
                      systemStatus.recent_alerts.map((alert: any, index: number) => (
                        <div key={index} className="p-3 border-b border-gray-100 last:border-b-0">
                          <div className="flex items-start space-x-3">
                            <div className={`w-2 h-2 rounded-full mt-2 ${
                              alert.level === 'high' ? 'bg-red-500' : 
                              alert.level === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                            }`} />
                            <div className="flex-1">
                              <p className="text-sm font-medium text-gray-900">{alert.message}</p>
                              <p className="text-xs text-gray-500 mt-1">{alert.timestamp}</p>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-4 text-center text-gray-500">
                        <p className="text-sm">No recent notifications</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* User Menu */}
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <User className="w-5 h-5 text-gray-600" />
              </div>
              <span className="text-sm text-gray-700">System Admin</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}; 