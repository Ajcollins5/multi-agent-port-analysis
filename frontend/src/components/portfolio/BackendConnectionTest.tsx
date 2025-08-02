import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Wifi, 
  WifiOff, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  RefreshCw,
  Server,
  Database,
  Zap
} from 'lucide-react';
import toast from 'react-hot-toast';

interface BackendStatus {
  backend_available: boolean;
  api_key_configured: boolean;
  database_connected: boolean;
  optimizations_active: boolean;
  response_time: number;
  version: string;
}

const BackendConnectionTest: React.FC = () => {
  const [testInProgress, setTestInProgress] = useState(false);

  const { data: backendStatus, refetch, isLoading } = useQuery<BackendStatus>({
    queryKey: ['backend-status'],
    queryFn: async () => {
      const response = await fetch('/api/backend/status');
      if (!response.ok) {
        throw new Error('Backend connection failed');
      }
      return response.json();
    },
    refetchInterval: 30000, // Check every 30 seconds
    retry: 1,
  });

  const runConnectionTest = async () => {
    setTestInProgress(true);
    try {
      await refetch();
      toast.success('Backend connection test completed');
    } catch (error) {
      toast.error('Backend connection test failed');
    } finally {
      setTestInProgress(false);
    }
  };

  const getStatusIcon = (status: boolean) => {
    return status ? (
      <CheckCircle className="w-5 h-5 text-green-600" />
    ) : (
      <XCircle className="w-5 h-5 text-red-600" />
    );
  };

  const getStatusColor = (status: boolean) => {
    return status ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
          <Server className="w-5 h-5 text-blue-600" />
          Backend Connection
        </h3>
        
        <button
          onClick={runConnectionTest}
          disabled={testInProgress || isLoading}
          className="flex items-center gap-2 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${(testInProgress || isLoading) ? 'animate-spin' : ''}`} />
          Test Connection
        </button>
      </div>

      {backendStatus ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wifi className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Backend Available</span>
            </div>
            <div className="flex items-center gap-2">
              {getStatusIcon(backendStatus.backend_available)}
              <span className={`text-sm font-medium ${getStatusColor(backendStatus.backend_available)}`}>
                {backendStatus.backend_available ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">API Key Configured</span>
            </div>
            <div className="flex items-center gap-2">
              {getStatusIcon(backendStatus.api_key_configured)}
              <span className={`text-sm font-medium ${getStatusColor(backendStatus.api_key_configured)}`}>
                {backendStatus.api_key_configured ? 'Configured' : 'Missing'}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Database Connected</span>
            </div>
            <div className="flex items-center gap-2">
              {getStatusIcon(backendStatus.database_connected)}
              <span className={`text-sm font-medium ${getStatusColor(backendStatus.database_connected)}`}>
                {backendStatus.database_connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-600">Optimizations Active</span>
            </div>
            <div className="flex items-center gap-2">
              {getStatusIcon(backendStatus.optimizations_active)}
              <span className={`text-sm font-medium ${getStatusColor(backendStatus.optimizations_active)}`}>
                {backendStatus.optimizations_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>

          <div className="pt-2 border-t border-gray-200">
            <div className="flex justify-between items-center text-xs text-gray-500">
              <span>Response Time: {backendStatus.response_time.toFixed(0)}ms</span>
              <span>Version: {backendStatus.version}</span>
            </div>
          </div>

          {!backendStatus.backend_available && (
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <div className="flex items-center gap-2 text-yellow-800">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm font-medium">Backend Unavailable</span>
              </div>
              <p className="text-xs text-yellow-700 mt-1">
                Using mock data for development. Start the Python backend for full functionality.
              </p>
            </div>
          )}

          {!backendStatus.api_key_configured && backendStatus.backend_available && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <div className="flex items-center gap-2 text-blue-800">
                <AlertTriangle className="w-4 h-4" />
                <span className="text-sm font-medium">API Key Required</span>
              </div>
              <p className="text-xs text-blue-700 mt-1">
                Add XAI_API_KEY to your .env file for real market data analysis.
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center gap-2 text-gray-500">
            <WifiOff className="w-5 h-5" />
            <span className="text-sm">Testing connection...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default BackendConnectionTest;
