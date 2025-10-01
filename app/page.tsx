'use client';

import { useState, useEffect } from 'react';
import { Star, RefreshCw, Send, Sparkles, BarChart3, History, Key, FileText } from 'lucide-react';

interface Review {
  reviewId: string;
  rating: number;
  userComment: string;
  language: string;
  device: string;
  appVersion: string | number;
  androidVersion: string | number;
  thumbsUp: number;
  hasReply: boolean;
  replyText: string;
}

interface AIPreview {
  response: string;
  length: number;
  language: string;
}

export default function Home() {
  const [packageName, setPackageName] = useState('com.nanobanana.app');
  const [configured, setConfigured] = useState(false);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedReview, setSelectedReview] = useState<Review | null>(null);
  const [aiPreview, setAIPreview] = useState<AIPreview | null>(null);
  const [customReply, setCustomReply] = useState('');
  const [activeTab, setActiveTab] = useState<'reviews' | 'stats' | 'history'>('reviews');
  
  // API credentials state
  const [serviceAccountData, setServiceAccountData] = useState('');
  const [geminiApiKey, setGeminiApiKey] = useState('');
  const [showCredentials, setShowCredentials] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL || (typeof window !== 'undefined' ? window.location.origin + '/api' : '/api');

  // Load saved credentials on mount
  useEffect(() => {
    const savedServiceAccount = localStorage.getItem('service_account_data');
    const savedGeminiKey = localStorage.getItem('gemini_api_key');
    const savedPackage = localStorage.getItem('package_name');
    
    if (savedServiceAccount) setServiceAccountData(savedServiceAccount);
    if (savedGeminiKey) setGeminiApiKey(savedGeminiKey);
    if (savedPackage) setPackageName(savedPackage);
  }, []);

  const configure = async () => {
    if (!serviceAccountData || !geminiApiKey) {
      alert('Please enter your API credentials first.');
      setShowCredentials(true);
      return;
    }

    setLoading(true);
    try {
      // Parse service account data
      let parsedServiceAccount;
      try {
        parsedServiceAccount = JSON.parse(serviceAccountData);
      } catch (err) {
        alert('Invalid JSON format for service account data');
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE}/configure`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          package_name: packageName, 
          enable_ai: true,
          service_account_data: parsedServiceAccount,
          gemini_api_key: geminiApiKey
        }),
      });
      const data = await response.json();
      if (data.success) {
        setConfigured(true);
        // Save credentials to localStorage
        localStorage.setItem('service_account_data', serviceAccountData);
        localStorage.setItem('gemini_api_key', geminiApiKey);
        localStorage.setItem('package_name', packageName);
        fetchReviews();
      } else {
        alert(data.message || 'Configuration failed');
      }
    } catch (error) {
      console.error('Configuration failed:', error);
      alert('Failed to configure. Make sure the backend is running.');
    }
    setLoading(false);
  };

  const fetchReviews = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/reviews?max_results=10`);
      const data = await response.json();
      if (data.success) {
        setReviews(data.reviews);
      }
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
    }
    setLoading(false);
  };

  const previewAIResponse = async (review: Review) => {
    setSelectedReview(review);
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/ai-preview`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          review_text: review.userComment,
          rating: review.rating,
          review_id: review.reviewId,
        }),
      });
      const data = await response.json();
      if (data.success) {
        setAIPreview(data);
        setCustomReply(data.response);
      }
    } catch (error) {
      console.error('Failed to preview AI response:', error);
    }
    setLoading(false);
  };

  const sendReply = async () => {
    if (!selectedReview || !customReply) return;
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/reply`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          review_id: selectedReview.reviewId,
          reply_text: customReply,
        }),
      });
      const data = await response.json();
      if (data.success) {
        alert('Reply sent successfully!');
        setSelectedReview(null);
        setAIPreview(null);
        setCustomReply('');
        fetchReviews();
      }
    } catch (error) {
      console.error('Failed to send reply:', error);
      alert('Failed to send reply');
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 dark:text-white mb-2">
            Google Play Reviews Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Manage your app reviews with AI-powered responses
          </p>
        </div>

        {/* API Credentials */}
        {!configured && (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
              API Credentials
            </h2>
            
            {/* Service Account Data */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Google Service Account JSON
              </label>
              <div className="space-y-2">
                <div className="relative">
                  <FileText className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <input
                    type="file"
                    accept=".json"
                    onChange={(e) => {
                      const file = e.target.files?.[0];
                      if (file) {
                        const reader = new FileReader();
                        reader.onload = (event) => {
                          const content = event.target?.result as string;
                          setServiceAccountData(content);
                        };
                        reader.readAsText(file);
                      }
                    }}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white file:mr-4 file:py-1 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>
                <textarea
                  value={serviceAccountData}
                  onChange={(e) => setServiceAccountData(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Or paste your service account JSON here..."
                  rows={4}
                />
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Upload your Google Cloud service account JSON file or paste the content
              </p>
            </div>

            {/* Gemini API Key */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Gemini API Key
              </label>
              <div className="relative">
                <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="password"
                  value={geminiApiKey}
                  onChange={(e) => setGeminiApiKey(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Enter your Gemini API key"
                />
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Get your API key from <a href="https://makersuite.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google AI Studio</a>
              </p>
            </div>

            {/* Package Name */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Package Name
              </label>
              <input
                type="text"
                value={packageName}
                onChange={(e) => setPackageName(e.target.value)}
                placeholder="com.example.app"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
              />
            </div>

            <button
              onClick={configure}
              disabled={loading || !serviceAccountData || !geminiApiKey}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Configuring...' : 'Configure & Start'}
            </button>
          </div>
        )}

        {configured && (
          <>
            {/* Tabs */}
            <div className="mb-6 flex gap-4 border-b border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setActiveTab('reviews')}
                className={`px-4 py-2 font-medium transition-colors ${
                  activeTab === 'reviews'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800 dark:text-gray-400'
                }`}
              >
                Reviews
              </button>
              <button
                onClick={() => setActiveTab('stats')}
                className={`px-4 py-2 font-medium transition-colors flex items-center gap-2 ${
                  activeTab === 'stats'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800 dark:text-gray-400'
                }`}
              >
                <BarChart3 size={20} />
                Stats
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-4 py-2 font-medium transition-colors flex items-center gap-2 ${
                  activeTab === 'history'
                    ? 'text-blue-600 border-b-2 border-blue-600'
                    : 'text-gray-600 hover:text-gray-800 dark:text-gray-400'
                }`}
              >
                <History size={20} />
                History
              </button>
            </div>

            {/* Reviews Tab */}
            {activeTab === 'reviews' && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Reviews List */}
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-semibold text-gray-800 dark:text-white">
                      Latest Reviews
                    </h2>
                    <button
                      onClick={fetchReviews}
                      disabled={loading}
                      className="p-2 bg-white dark:bg-gray-800 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors shadow"
                    >
                      <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
                    </button>
                  </div>

                  <div className="space-y-4">
                    {reviews.map((review) => (
                      <div
                        key={review.reviewId}
                        className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow cursor-pointer"
                        onClick={() => previewAIResponse(review)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <div className="flex items-center gap-2">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                size={16}
                                className={i < review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}
                              />
                            ))}
                          </div>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {review.language.toUpperCase()}
                          </span>
                        </div>
                        <p className="text-gray-700 dark:text-gray-300 mb-2">
                          {review.userComment}
                        </p>
                        <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                          <span>{review.device}</span>
                          <span>v{review.appVersion}</span>
                          <span>Android {review.androidVersion}</span>
                        </div>
                        {review.hasReply && (
                          <div className="mt-2 text-xs text-green-600 dark:text-green-400">
                            ✓ Already replied
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI Preview */}
                <div>
                  {selectedReview ? (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2 text-gray-800 dark:text-white">
                        <Sparkles className="text-blue-600" size={24} />
                        AI Response Preview
                      </h3>

                      <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          Original Review ({selectedReview.rating} stars):
                        </p>
                        <p className="text-gray-800 dark:text-white">
                          {selectedReview.userComment}
                        </p>
                      </div>

                      {aiPreview && (
                        <div className="mb-4">
                          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">
                            Language: {aiPreview.language} | Length: {aiPreview.length}/350 characters
                          </p>
                        </div>
                      )}

                      <textarea
                        value={customReply}
                        onChange={(e) => setCustomReply(e.target.value)}
                        className="w-full h-32 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white mb-4"
                        placeholder="Edit AI response or write your own..."
                      />

                      <div className="flex gap-4">
                        <button
                          onClick={sendReply}
                          disabled={loading || !customReply}
                          className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
                        >
                          <Send size={20} />
                          Send Reply
                        </button>
                        <button
                          onClick={() => {
                            setSelectedReview(null);
                            setAIPreview(null);
                            setCustomReply('');
                          }}
                          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 text-center text-gray-500 dark:text-gray-400">
                      <Sparkles size={48} className="mx-auto mb-4 text-gray-300 dark:text-gray-600" />
                      <p>Select a review to preview AI response</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Stats Tab */}
            {activeTab === 'stats' && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
                  Statistics
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Stats will be displayed here...
                </p>
              </div>
            )}

            {/* History Tab */}
            {activeTab === 'history' && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
                  Reply History
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  History will be displayed here...
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
