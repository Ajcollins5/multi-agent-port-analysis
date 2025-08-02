import React, { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import NewsIntelligenceDashboard from '../components/news/NewsIntelligenceDashboard';
import AutomatedPipelineDashboard from '../components/news/AutomatedPipelineDashboard';
import { Brain, Zap, BarChart3, Newspaper } from 'lucide-react';

const NewsIntelligence: React.FC = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handlePipelineUpdate = () => {
    // Trigger refresh of dashboard when pipeline processes new articles
    setRefreshTrigger(prev => prev + 1);
    // Switch to dashboard to see the new data
    setActiveTab('dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Brain className="w-8 h-8 text-blue-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">News Intelligence Platform</h1>
              <p className="text-gray-600 mt-1">
                Compress news articles into temporal snapshots and analyze stock personality patterns
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'dashboard'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Intelligence Dashboard
              </div>
            </button>
            
            <button
              onClick={() => setActiveTab('pipeline')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'pipeline'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4" />
                Automated Pipeline
              </div>
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="py-8">
        {activeTab === 'dashboard' && (
          <NewsIntelligenceDashboard key={refreshTrigger} />
        )}

        {activeTab === 'pipeline' && (
          <AutomatedPipelineDashboard />
        )}
      </div>

      {/* Feature Overview */}
      {activeTab === 'dashboard' && (
        <div className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                How News Intelligence Works
              </h2>
              <p className="text-gray-600 max-w-3xl mx-auto">
                Our AI system compresses news articles into 2-sentence snapshots, capturing the essence 
                of market events and their impact on stock prices. Over time, this builds a personality 
                profile for each stock.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Automated Ingestion</h3>
                <p className="text-gray-600 text-sm">
                  Financial Modeling Prep API automatically fetches latest news articles for monitored stocks.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-time Impact</h3>
                <p className="text-gray-600 text-sm">
                  Price changes are tracked automatically 1h and 24h after news publication.
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Brain className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Enrichment</h3>
                <p className="text-gray-600 text-sm">
                  Grok 4 AI analyzes and compresses articles into 2-sentence summaries with deep insights.
                </p>
              </div>
            </div>

            <div className="mt-12 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8">
              <div className="text-center">
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  The Goal: Stock Personality Intelligence
                </h3>
                <p className="text-gray-700 max-w-4xl mx-auto">
                  The automated pipeline continuously monitors news sources and processes articles in real-time.
                  After a year of operation, we'll have 200+ compressed snapshots per stock, creating unique
                  "personality profiles" that show how each stock typically reacts to different types of news.
                  This enables predictive analysis and automated trading insights.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default NewsIntelligence;
