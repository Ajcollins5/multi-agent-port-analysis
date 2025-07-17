import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: LucideIcon;
  subtitle?: string;
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  subtitle,
  className = ''
}) => {
  const getChangeColor = (type: string) => {
    switch (type) {
      case 'positive':
        return 'text-success-600';
      case 'negative':
        return 'text-error-600';
      default:
        return 'text-gray-600';
    }
  };

  const getChangeIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return '↗';
      case 'negative':
        return '↘';
      default:
        return '→';
    }
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-6 shadow-card hover:shadow-card-hover transition-shadow ${className}`}>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="flex items-center space-x-2">
            {Icon && (
              <div className="p-2 bg-primary-50 rounded-lg">
                <Icon className="w-5 h-5 text-primary-600" />
              </div>
            )}
            <div>
              <p className="text-sm font-medium text-gray-600">{title}</p>
              {subtitle && (
                <p className="text-xs text-gray-500">{subtitle}</p>
              )}
            </div>
          </div>
        </div>
      </div>
      
      <div className="mt-4">
        <div className="flex items-baseline space-x-2">
          <span className="text-2xl font-bold text-gray-900">{value}</span>
          {change !== undefined && (
            <span className={`text-sm font-medium ${getChangeColor(changeType)} flex items-center space-x-1`}>
              <span>{getChangeIcon(changeType)}</span>
              <span>{Math.abs(change)}%</span>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}; 