import React, { useState } from 'react';
import { Layout } from '@/components/layout/Layout';
import { MetricCard } from '@/components/common/MetricCard';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';
import { ErrorMessage } from '@/components/common/ErrorMessage';
import { useSendEmail, useSystemStatus } from '@/hooks/useApi';
import { POPULAR_STOCKS } from '@/utils/api';
import { 
  Settings as SettingsIcon, 
  Mail, 
  Database, 
  Cpu,
  Shield,
  Bell,
  Download,
  Upload,
  Trash2,
  Check,
  X,
  AlertTriangle,
  Info
} from 'lucide-react';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState('general');
  const [portfolio, setPortfolio] = useState(['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']);
  const [newTicker, setNewTicker] = useState('');
  const [emailSubject, setEmailSubject] = useState('Test Email from Portfolio Analysis');
  const [emailMessage, setEmailMessage] = useState('This is a test email from the Multi-Agent Portfolio Analysis system.');
  
  const sendEmail = useSendEmail();
  const { data: systemStatus, refetch: refreshSystemStatus } = useSystemStatus();

  const handleAddTicker = () => {
    const ticker = newTicker.trim().toUpperCase();
    if (ticker && !portfolio.includes(ticker)) {
      setPortfolio([...portfolio, ticker]);
      setNewTicker('');
    }
  };

  const handleRemoveTicker = (ticker: string) => {
    setPortfolio(portfolio.filter(t => t !== ticker));
  };

  const handleSendTestEmail = async () => {
    await sendEmail.mutateAsync({
      subject: emailSubject,
      message: emailMessage
    });
  };

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'portfolio', label: 'Portfolio', icon: Database },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'system', label: 'System', icon: Cpu },
    { id: 'security', label: 'Security', icon: Shield }
  ];

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600">Configure your portfolio analysis system</p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg border border-gray-200">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map(tab => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                      activeTab === tab.id
                        ? 'border-primary-500 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {/* General Settings */}
            {activeTab === 'general' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">General Settings</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Application Theme
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                        <option>Light</option>
                        <option>Dark</option>
                        <option>System</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Default Dashboard View
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                        <option>Portfolio Overview</option>
                        <option>Recent Insights</option>
                        <option>Market Summary</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Refresh Interval (seconds)
                      </label>
                      <input
                        type="number"
                        min="10"
                        max="3600"
                        defaultValue="30"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Currency Display
                      </label>
                      <select className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent">
                        <option>USD ($)</option>
                        <option>EUR (€)</option>
                        <option>GBP (£)</option>
                        <option>JPY (¥)</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end space-x-3">
                  <button className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                    Reset to Defaults
                  </button>
                  <button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
                    Save Changes
                  </button>
                </div>
              </div>
            )}

            {/* Portfolio Settings */}
            {activeTab === 'portfolio' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Portfolio Management</h3>
                  
                  {/* Current Portfolio */}
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Current Portfolio</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2">
                      {portfolio.map(ticker => (
                        <div key={ticker} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm font-medium text-gray-900">{ticker}</span>
                          <button
                            onClick={() => handleRemoveTicker(ticker)}
                            className="text-error-600 hover:text-error-700"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Add New Ticker */}
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Add New Ticker</h4>
                    <div className="flex items-center space-x-3">
                      <input
                        type="text"
                        value={newTicker}
                        onChange={(e) => setNewTicker(e.target.value.toUpperCase())}
                        placeholder="Enter ticker symbol"
                        className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      />
                      <button
                        onClick={handleAddTicker}
                        className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                      >
                        Add
                      </button>
                    </div>
                  </div>

                  {/* Quick Add Popular Stocks */}
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Quick Add Popular Stocks</h4>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                      {POPULAR_STOCKS.slice(0, 10).map(stock => (
                        <button
                          key={stock.ticker}
                          onClick={() => {
                            if (!portfolio.includes(stock.ticker)) {
                              setPortfolio([...portfolio, stock.ticker]);
                            }
                          }}
                          disabled={portfolio.includes(stock.ticker)}
                          className={`p-2 text-left border rounded-lg text-sm ${
                            portfolio.includes(stock.ticker)
                              ? 'border-success-300 bg-success-50 text-success-700'
                              : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50'
                          }`}
                        >
                          {portfolio.includes(stock.ticker) && (
                            <Check className="w-4 h-4 text-success-600 float-right" />
                          )}
                          <div className="font-medium">{stock.ticker}</div>
                          <div className="text-xs text-gray-500">{stock.name}</div>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end space-x-3">
                  <button className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50">
                    Export Portfolio
                  </button>
                  <button className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700">
                    Save Portfolio
                  </button>
                </div>
              </div>
            )}

            {/* Notifications Settings */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Settings</h3>
                  
                  {/* Email Settings */}
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Email Notifications</h4>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">High Impact Alerts</p>
                          <p className="text-xs text-gray-500">Receive emails for volatility events &gt;5%</p>
                        </div>
                        <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600 rounded" />
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">Daily Summaries</p>
                          <p className="text-xs text-gray-500">Daily portfolio analysis summaries</p>
                        </div>
                        <input type="checkbox" defaultChecked className="h-4 w-4 text-primary-600 rounded" />
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-900">System Alerts</p>
                          <p className="text-xs text-gray-500">System maintenance and updates</p>
                        </div>
                        <input type="checkbox" className="h-4 w-4 text-primary-600 rounded" />
                      </div>
                    </div>
                  </div>

                  {/* Test Email */}
                  <div className="mb-6">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Test Email Configuration</h4>
                    <div className="space-y-3">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Subject</label>
                        <input
                          type="text"
                          value={emailSubject}
                          onChange={(e) => setEmailSubject(e.target.value)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                        <textarea
                          value={emailMessage}
                          onChange={(e) => setEmailMessage(e.target.value)}
                          rows={4}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        />
                      </div>
                      <button
                        onClick={handleSendTestEmail}
                        disabled={sendEmail.isLoading}
                        className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 disabled:opacity-50"
                      >
                        {sendEmail.isLoading ? (
                          <LoadingSpinner size="sm" />
                        ) : (
                          <Mail className="w-4 h-4" />
                        )}
                        <span>Send Test Email</span>
                      </button>
                    </div>

                    {sendEmail.isSuccess && (
                      <div className="mt-3 p-3 bg-success-50 border border-success-200 rounded-md">
                        <div className="flex items-center space-x-2">
                          <Check className="w-4 h-4 text-success-600" />
                          <span className="text-sm text-success-800">Test email sent successfully!</span>
                        </div>
                      </div>
                    )}

                    {sendEmail.isError && (
                      <div className="mt-3">
                        <ErrorMessage
                          title="Email Error"
                          message={sendEmail.error?.message || 'Failed to send test email'}
                          onRetry={handleSendTestEmail}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* System Settings */}
            {activeTab === 'system' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">System Information</h3>
                  
                  {/* System Status */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                    <MetricCard
                      title="System Status"
                      value={systemStatus?.success ? 'Online' : 'Offline'}
                      icon={systemStatus?.success ? Check : X}
                      changeType={systemStatus?.success ? 'positive' : 'negative'}
                    />
                    <MetricCard
                      title="API Version"
                      value={systemStatus?.data?.version || 'Unknown'}
                      icon={Info}
                    />
                    <MetricCard
                      title="Framework"
                      value={systemStatus?.data?.framework || 'Flask'}
                      icon={Cpu}
                    />
                  </div>

                  {/* System Actions */}
                  <div className="space-y-4">
                    <h4 className="text-sm font-medium text-gray-700">System Actions</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <button
                        onClick={refreshSystemStatus}
                        className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                      >
                        <SettingsIcon className="w-4 h-4" />
                        <span>Refresh System Status</span>
                      </button>
                      <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
                        <Download className="w-4 h-4" />
                        <span>Export System Logs</span>
                      </button>
                      <button className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50">
                        <Database className="w-4 h-4" />
                        <span>Clear Cache</span>
                      </button>
                      <button className="flex items-center space-x-2 px-4 py-2 border border-error-300 text-error-600 rounded-md hover:bg-error-50">
                        <Trash2 className="w-4 h-4" />
                        <span>Clear All Data</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Security Settings */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Security Settings</h3>
                  
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="w-5 h-5 text-yellow-600" />
                      <h4 className="text-sm font-medium text-yellow-800">Security Configuration</h4>
                    </div>
                    <p className="text-sm text-yellow-700 mt-1">
                      Security settings are managed through environment variables. 
                      Contact your system administrator for changes.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">API Key Protection</p>
                        <p className="text-xs text-gray-500">API keys are securely stored as environment variables</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Check className="w-4 h-4 text-success-600" />
                        <span className="text-sm text-success-600">Enabled</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">HTTPS Encryption</p>
                        <p className="text-xs text-gray-500">All communications are encrypted in transit</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Check className="w-4 h-4 text-success-600" />
                        <span className="text-sm text-success-600">Enabled</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-900">Rate Limiting</p>
                        <p className="text-xs text-gray-500">API requests are rate limited for security</p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Check className="w-4 h-4 text-success-600" />
                        <span className="text-sm text-success-600">Enabled</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Save Changes Button */}
        <div className="flex justify-end">
          <button className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
            Save All Changes
          </button>
        </div>
      </div>
    </Layout>
  );
};

export default Settings; 