import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { 
  BarChart3, 
  Search, 
  Brain, 
  Bell, 
  Settings, 
  Activity,
  TrendingUp,
  Clock
} from 'lucide-react';

const navigationItems = [
  {
    name: 'Portfolio Dashboard',
    href: '/',
    icon: BarChart3,
    description: 'Real-time portfolio metrics and overview'
  },
  {
    name: 'Ad-hoc Analysis',
    href: '/analysis',
    icon: Search,
    description: 'Analyze individual stocks'
  },
  {
    name: 'Knowledge Evolution',
    href: '/knowledge',
    icon: Brain,
    description: 'Historical insights and learning'
  },
  {
    name: 'Event Monitoring',
    href: '/events',
    icon: Bell,
    description: 'Real-time alerts and notifications'
  },
  {
    name: 'Background Scheduling',
    href: '/scheduler',
    icon: Clock,
    description: 'Automated analysis configuration'
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'System configuration and preferences'
  }
];

export const Sidebar: React.FC = () => {
  const router = useRouter();

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo and title */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-primary-100 rounded-lg">
            <TrendingUp className="w-6 h-6 text-primary-600" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gray-900">
              Portfolio Analysis
            </h1>
            <p className="text-sm text-gray-500">
              Multi-Agent System
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = router.pathname === item.href;
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`
                flex items-center space-x-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                ${isActive 
                  ? 'bg-primary-50 text-primary-700 border-l-4 border-primary-500' 
                  : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }
              `}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : 'text-gray-400'}`} />
              <div className="flex-1">
                <div className="font-medium">{item.name}</div>
                <div className="text-xs text-gray-500">{item.description}</div>
              </div>
            </Link>
          );
        })}
      </nav>

      {/* System status */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-2 text-sm">
          <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
          <span className="text-gray-600">System Active</span>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Powered by Grok 4 AI
        </div>
      </div>
    </div>
  );
}; 