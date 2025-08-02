import React, { useState } from 'react';
import { Upload, Newspaper, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';

interface NewsIngestionFormProps {
  onArticleIngested?: (snapshot: any) => void;
}

const NewsIngestionForm: React.FC<NewsIngestionFormProps> = ({ onArticleIngested }) => {
  const [formData, setFormData] = useState({
    ticker: '',
    article_text: '',
    source_url: '',
    price_before: '',
    price_1h_after: '',
    price_24h_after: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastSnapshot, setLastSnapshot] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await fetch('/api/app_supabase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'ingest_news_article',
          ticker: formData.ticker.toUpperCase(),
          article_text: formData.article_text,
          source_url: formData.source_url,
          price_before: parseFloat(formData.price_before),
          price_1h_after: parseFloat(formData.price_1h_after),
          price_24h_after: parseFloat(formData.price_24h_after)
        })
      });

      const result = await response.json();
      
      if (result.success) {
        setLastSnapshot(result.snapshot);
        toast.success('News article ingested successfully!');
        
        // Reset form
        setFormData({
          ticker: '',
          article_text: '',
          source_url: '',
          price_before: '',
          price_1h_after: '',
          price_24h_after: ''
        });

        if (onArticleIngested) {
          onArticleIngested(result.snapshot);
        }
      } else {
        toast.error(`Failed to ingest article: ${result.error}`);
      }
    } catch (error) {
      console.error('Error ingesting article:', error);
      toast.error('Failed to ingest article');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const calculatePriceChange = (before: number, after: number) => {
    if (!before || !after) return 0;
    return ((after - before) / before) * 100;
  };

  const priceChange1h = calculatePriceChange(
    parseFloat(formData.price_before), 
    parseFloat(formData.price_1h_after)
  );
  
  const priceChange24h = calculatePriceChange(
    parseFloat(formData.price_before), 
    parseFloat(formData.price_24h_after)
  );

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center gap-3 mb-6">
          <Upload className="w-6 h-6 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">News Article Ingestion</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Ticker and URLs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Stock Ticker *
              </label>
              <input
                type="text"
                value={formData.ticker}
                onChange={(e) => handleInputChange('ticker', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="AAPL"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Source URL
              </label>
              <input
                type="url"
                value={formData.source_url}
                onChange={(e) => handleInputChange('source_url', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://example.com/news-article"
              />
            </div>
          </div>

          {/* Price Data */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Price Before News *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.price_before}
                onChange={(e) => handleInputChange('price_before', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="150.00"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Price 1 Hour After *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.price_1h_after}
                onChange={(e) => handleInputChange('price_1h_after', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="152.50"
                required
              />
              {priceChange1h !== 0 && (
                <div className={`text-xs mt-1 ${priceChange1h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {priceChange1h >= 0 ? '+' : ''}{priceChange1h.toFixed(2)}%
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Price 24 Hours After *
              </label>
              <input
                type="number"
                step="0.01"
                value={formData.price_24h_after}
                onChange={(e) => handleInputChange('price_24h_after', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="155.00"
                required
              />
              {priceChange24h !== 0 && (
                <div className={`text-xs mt-1 ${priceChange24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {priceChange24h >= 0 ? '+' : ''}{priceChange24h.toFixed(2)}%
                </div>
              )}
            </div>
          </div>

          {/* Article Text */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Article Text *
            </label>
            <textarea
              value={formData.article_text}
              onChange={(e) => handleInputChange('article_text', e.target.value)}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Paste the full news article text here..."
              required
            />
            <div className="text-xs text-gray-500 mt-1">
              {formData.article_text.length} characters
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Processing...
                </>
              ) : (
                <>
                  <Newspaper className="w-4 h-4" />
                  Ingest Article
                </>
              )}
            </button>
          </div>
        </form>

        {/* Last Snapshot Preview */}
        {lastSnapshot && (
          <div className="mt-8 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-2 mb-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <h3 className="font-medium text-green-800">Article Successfully Compressed</h3>
            </div>
            
            <div className="space-y-2 text-sm">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                <div>
                  <span className="font-medium">Category:</span> {lastSnapshot.category.replace('_', ' ')}
                </div>
                <div>
                  <span className="font-medium">Impact:</span> {lastSnapshot.impact.replace('_', ' ')}
                </div>
                <div>
                  <span className="font-medium">Confidence:</span> {(lastSnapshot.confidence_score * 100).toFixed(0)}%
                </div>
              </div>
              
              <div className="space-y-1">
                <p><span className="font-medium">Summary Line 1:</span> {lastSnapshot.summary_line_1}</p>
                <p><span className="font-medium">Summary Line 2:</span> {lastSnapshot.summary_line_2}</p>
              </div>
              
              <div className="flex gap-4 text-xs text-gray-600 mt-2">
                <span>1h: {lastSnapshot.price_change_1h >= 0 ? '+' : ''}{lastSnapshot.price_change_1h.toFixed(2)}%</span>
                <span>24h: {lastSnapshot.price_change_24h >= 0 ? '+' : ''}{lastSnapshot.price_change_24h.toFixed(2)}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-800">
              <p className="font-medium mb-1">How it works:</p>
              <ul className="space-y-1 text-blue-700">
                <li>• Paste a news article about a stock</li>
                <li>• Provide price data before and after the news</li>
                <li>• The AI will compress the article into 2 sentences</li>
                <li>• Creates a temporal snapshot for personality analysis</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewsIngestionForm;
