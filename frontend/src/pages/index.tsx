import React, { useState } from 'react';
import Link from 'next/link';
import PortfolioManager from '@/components/portfolio/PortfolioManager';
import { Brain, BarChart3, Newspaper, TrendingUp } from 'lucide-react';

const HomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">AI Portfolio Manager</h1>
            </div>

            <nav className="flex space-x-4">
              <Link
                href="/"
                className="px-4 py-2 text-blue-600 bg-blue-50 rounded-md font-medium"
              >
                <div className="flex items-center gap-2">
                  <BarChart3 className="w-4 h-4" />
                  Portfolio Analysis
                </div>
              </Link>

              <Link
                href="/NewsIntelligence"
                className="px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-md font-medium transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Brain className="w-4 h-4" />
                  News Intelligence
                </div>
              </Link>
            </nav>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <PortfolioManager />

      {/* Feature Highlight */}
      <div className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Platform Features
            </h2>
            <p className="text-gray-600 max-w-3xl mx-auto">
              Advanced AI-powered portfolio analysis with continuous monitoring and news intelligence
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <BarChart3 className="w-8 h-8 text-blue-600" />
                <h3 className="text-xl font-semibold text-gray-900">Portfolio Analysis</h3>
              </div>
              <p className="text-gray-700 mb-4">
                Real-time AI analysis of your portfolio with 5-year price targets, risk assessment,
                and continuous monitoring at your preferred frequency.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Continuous monitoring (hourly, daily, weekly)</li>
                <li>• AI-powered risk assessment</li>
                <li>• 5-year price targets with confidence scores</li>
                <li>• Cost-aware analysis scheduling</li>
              </ul>
            </div>

            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6">
              <div className="flex items-center gap-3 mb-4">
                <Brain className="w-8 h-8 text-purple-600" />
                <h3 className="text-xl font-semibold text-gray-900">News Intelligence</h3>
              </div>
              <p className="text-gray-700 mb-4">
                Compress news articles into 2-sentence snapshots and build stock personality
                profiles based on historical reactions to different types of news.
              </p>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Article compression to 2 sentences</li>
                <li>• Temporal impact analysis</li>
                <li>• Stock personality profiling</li>
                <li>• Predictive news reaction modeling</li>
              </ul>
              <Link
                href="/NewsIntelligence"
                className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors"
              >
                <Newspaper className="w-4 h-4" />
                Try News Intelligence
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;