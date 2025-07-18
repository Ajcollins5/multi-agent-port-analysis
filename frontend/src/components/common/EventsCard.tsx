import React, { useState } from 'react';
import { AlertTriangle, Info, CheckCircle, XCircle, Clock, Filter, Search } from 'lucide-react';
import { Event } from '@/types';
import { getImpactColor, formatShortDate } from '@/utils/api';

interface EventsCardProps {
  events: Event[];
  totalCount: number;
  onFilterChange?: (filters: any) => void;
  className?: string;
  showFilters?: boolean;
  maxEvents?: number;
}

export const EventsCard: React.FC<EventsCardProps> = ({ 
  events, 
  totalCount, 
  onFilterChange, 
  className = '', 
  showFilters = true,
  maxEvents = 10
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');

  const getEventIcon = (type: string) => {
    switch (type?.toUpperCase()) {
      case 'SUCCESS':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'WARNING':
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
      case 'ERROR':
      case 'CRITICAL':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'INFO':
        return <Info className="w-4 h-4 text-blue-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getEventTypeColor = (type: string) => {
    switch (type?.toUpperCase()) {
      case 'SUCCESS':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'WARNING':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'ERROR':
      case 'CRITICAL':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'INFO':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const filteredEvents = events.filter(event => {
    const matchesSearch = !searchTerm || 
      event.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      event.ticker.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesSeverity = !severityFilter || event.severity === severityFilter;
    const matchesType = !typeFilter || event.type === typeFilter;
    
    return matchesSearch && matchesSeverity && matchesType;
  }).slice(0, maxEvents);

  const handleFilterChange = (key: string, value: string) => {
    const newFilters = { [key]: value };
    if (onFilterChange) {
      onFilterChange(newFilters);
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Events</h3>
          <p className="text-sm text-gray-500">
            {totalCount > 0 ? `${filteredEvents.length} of ${totalCount} events` : 'No events'}
          </p>
        </div>
        {showFilters && (
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-600">Filters</span>
          </div>
        )}
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="mb-4 space-y-3">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
            <input
              type="text"
              placeholder="Search events..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Filter selects */}
          <div className="grid grid-cols-2 gap-3">
            <select
              value={severityFilter}
              onChange={(e) => {
                setSeverityFilter(e.target.value);
                handleFilterChange('severity', e.target.value);
              }}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Severities</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
            </select>

            <select
              value={typeFilter}
              onChange={(e) => {
                setTypeFilter(e.target.value);
                handleFilterChange('type', e.target.value);
              }}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Types</option>
              <option value="SUCCESS">Success</option>
              <option value="INFO">Info</option>
              <option value="WARNING">Warning</option>
              <option value="ERROR">Error</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>
        </div>
      )}

      {/* Events List */}
      <div className="space-y-3">
        {filteredEvents.length === 0 ? (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No events to display</p>
          </div>
        ) : (
          filteredEvents.map((event) => (
            <div key={event.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getEventIcon(event.type)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium text-gray-900">{event.ticker}</span>
                      <div className={`px-2 py-1 rounded-full text-xs font-medium ${getEventTypeColor(event.type)}`}>
                        {event.type}
                      </div>
                      {event.severity && (
                        <div className={`px-2 py-1 rounded-full text-xs font-medium ${getImpactColor(event.severity)}`}>
                          {event.severity}
                        </div>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 mb-2">{event.message}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <span>{formatShortDate(event.timestamp)}</span>
                      {event.agent && (
                        <span className="flex items-center">
                          <span className="w-2 h-2 bg-blue-400 rounded-full mr-1"></span>
                          {event.agent}
                        </span>
                      )}
                      {event.event_type && (
                        <span className="px-2 py-1 bg-gray-100 rounded text-gray-600">
                          {event.event_type}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Show More Button */}
      {events.length > maxEvents && (
        <div className="mt-4 text-center">
          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
            Show {Math.min(events.length - maxEvents, 10)} more events
          </button>
        </div>
      )}
    </div>
  );
}; 