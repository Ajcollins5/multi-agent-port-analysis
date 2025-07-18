import React from 'react';
import { CheckCircle, AlertCircle, XCircle, Clock, Database, Server, Mail, Calendar } from 'lucide-react';
import { SystemStatus } from '@/types';
import { getStatusColor, formatDate } from '@/utils/api';

interface SystemStatusCardProps {
  status: SystemStatus;
  className?: string;
}

export const SystemStatusCard: React.FC<SystemStatusCardProps> = ({ status, className = '' }) => {
  const getStatusIcon = (statusValue: string) => {
    switch (statusValue?.toLowerCase()) {
      case 'healthy':
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'degraded':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'unhealthy':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getServiceIcon = (service: string) => {
    switch (service) {
      case 'database':
        return <Database className="w-4 h-4" />;
      case 'supabase_manager':
        return <Server className="w-4 h-4" />;
      case 'email_service':
        return <Mail className="w-4 h-4" />;
      case 'scheduler':
        return <Calendar className="w-4 h-4" />;
      default:
        return <Server className="w-4 h-4" />;
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
        {getStatusIcon(status.status)}
      </div>

      {/* Overall Status */}
      <div className="mb-6">
        <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status.status)}`}>
          {status.status?.toUpperCase()}
        </div>
        <p className="text-sm text-gray-500 mt-1">
          Last updated: {formatDate(status.timestamp)}
        </p>
      </div>

      {/* Services Status */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-700">Services</h4>
        
        {/* Database */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Database className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-700">Database</span>
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(status.database)}`}>
            {status.database}
          </div>
        </div>

        {/* Supabase Manager */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Server className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-700">Supabase Manager</span>
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
            status.services.supabase_manager ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'
          }`}>
            {status.services.supabase_manager ? 'Connected' : 'Disconnected'}
          </div>
        </div>

        {/* Risk Agent */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Server className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-700">Risk Agent</span>
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
            status.services.supabase_risk_agent ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'
          }`}>
            {status.services.supabase_risk_agent ? 'Available' : 'Unavailable'}
          </div>
        </div>

        {/* Supervisor */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Server className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-700">Supervisor</span>
          </div>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
            status.services.supervisor ? 'text-green-600 bg-green-50' : 'text-red-600 bg-red-50'
          }`}>
            {status.services.supervisor ? 'Available' : 'Unavailable'}
          </div>
        </div>
      </div>

      {/* Environment Status */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <h4 className="text-sm font-medium text-gray-700 mb-2">Environment</h4>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Configuration</span>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
            status.environment.required_vars_present ? 'text-green-600 bg-green-50' : 'text-yellow-600 bg-yellow-50'
          }`}>
            {status.environment.required_vars_present ? 'Complete' : 'Incomplete'}
          </div>
        </div>
        
        {!status.environment.required_vars_present && status.environment.missing_vars.length > 0 && (
          <div className="mt-2 p-2 bg-yellow-50 rounded text-xs">
            <p className="text-yellow-700 font-medium">Missing Environment Variables:</p>
            <ul className="text-yellow-600 mt-1 space-y-1">
              {status.environment.missing_vars.map((variable, index) => (
                <li key={index} className="flex items-center">
                  <span className="w-2 h-2 bg-yellow-400 rounded-full mr-2"></span>
                  {variable}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Performance Metrics (if available) */}
      {status.performance_metrics && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Performance</h4>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {status.performance_metrics.response_time}ms
              </div>
              <div className="text-xs text-gray-500">Response Time</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {status.performance_metrics.memory_usage}%
              </div>
              <div className="text-xs text-gray-500">Memory Usage</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-900">
                {status.performance_metrics.cpu_usage}%
              </div>
              <div className="text-xs text-gray-500">CPU Usage</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 