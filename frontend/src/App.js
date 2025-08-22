import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Constants
const SESSION_STORAGE_KEY = 'financebot_session';
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const [marketData, setMarketData] = useState({});
  const [portfolio, setPortfolio] = useState(null);
  const [userName, setUserName] = useState('Guest');
  const [error, setError] = useState(null);
  const chatEndRef = useRef(null);
  const retryTimeoutRef = useRef(null);

  // Initialize session and load data
  useEffect(() => {
    const initializeApp = async () => {
      // Try to restore session from localStorage
      const savedSessionId = localStorage.getItem(SESSION_STORAGE_KEY);
      const newSessionId = savedSessionId || generateSessionId();
      setSessionId(newSessionId);
      localStorage.setItem(SESSION_STORAGE_KEY, newSessionId);
      
      try {
        // Load market data
        await fetchMarketData();
        
        // Load portfolio
        await fetchPortfolio('user123'); // Mock user ID
        
        // Load chat history if session exists
        if (savedSessionId) {
          await loadChatHistory(newSessionId);
        } else {
          // Add welcome message for new sessions
          addWelcomeMessage();
        }
        
        setConnectionStatus('connected');
      } catch (error) {
        console.error('Initialization error:', error);
        setConnectionStatus('error');
        setError('Failed to initialize application. Please refresh the page.');
      }
    };
    
    initializeApp();
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  const addWelcomeMessage = () => {
    setChatMessages([{
      role: 'assistant',
      content: `👋 **Welcome to FinanceBot Pro!**

I'm your AI Financial Advisor, powered by advanced financial AI technology. I'm here to help you with:

• **Investment Strategy** - Personalized portfolio recommendations and asset allocation
• **Market Analysis** - Real-time insights, trends, and market commentary  
• **Risk Management** - Risk assessment and mitigation strategies
• **Financial Planning** - Retirement planning, tax-efficient strategies, and wealth building
• **Portfolio Optimization** - Advanced optimization using modern portfolio theory

I can analyze your financial situation, recommend investment strategies, and help you make informed decisions about your financial future.

**What would you like to discuss about your financial goals today?**`,
      timestamp: new Date(),
      id: generateMessageId()
    }]);
  };

  const loadChatHistory = async (sessionId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/chat-history/${sessionId}`);
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'success' && data.data.length > 0) {
          const messages = data.data.map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp),
            id: generateMessageId()
          }));
          setChatMessages(messages);
        } else {
          addWelcomeMessage();
        }
      } else {
        addWelcomeMessage();
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      addWelcomeMessage();
    }
  };

  const generateMessageId = () => {
    return 'msg_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  };

  const generateSessionId = () => {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  };

  const fetchWithRetry = async (url, options = {}, retries = MAX_RETRIES) => {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, {
          ...options,
          timeout: 30000 // 30 second timeout
        });
        
        if (response.ok) {
          return response;
        } else if (response.status >= 500 && i < retries - 1) {
          // Retry on server errors
          await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (i + 1)));
          continue;
        } else {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (error) {
        if (i === retries - 1) {
          throw error;
        }
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY * (i + 1)));
      }
    }
  };

  const fetchMarketData = async () => {
    try {
      setConnectionStatus('loading');
      const response = await fetchWithRetry(`${BACKEND_URL}/api/market-data`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setMarketData(data.data);
        setConnectionStatus('connected');
      } else {
        throw new Error('Invalid market data response');
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
      setConnectionStatus('error');
      // Use fallback data
      setMarketData({
        "AAPL": {"price": 195.30, "change": "+2.45", "change_percent": "+1.27%"},
        "GOOGL": {"price": 2875.20, "change": "-15.30", "change_percent": "-0.53%"},
        "MSFT": {"price": 415.75, "change": "+3.20", "change_percent": "+0.78%"}
      });
    }
  };

  const fetchPortfolio = async (userId) => {
    try {
      const response = await fetchWithRetry(`${BACKEND_URL}/api/portfolio/${userId}`);
      const data = await response.json();
      
      if (data.status === 'success') {
        setPortfolio(data.data);
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      // Use fallback portfolio data
      setPortfolio({
        user_id: userId,
        assets: [
          {"symbol": "AAPL", "shares": 10, "avg_price": 190.50, "current_price": 195.30},
          {"symbol": "GOOGL", "shares": 2, "avg_price": 2800.00, "current_price": 2875.20},
          {"symbol": "MSFT", "shares": 5, "avg_price": 400.00, "current_price": 415.75}
        ],
        total_value: 8727.25,
        performance: {"total_return": "+5.2%", "daily_change": "+1.1%"}
      });
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const messageId = generateMessageId();
    const userMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date(),
      id: messageId
    };

    setChatMessages(prev => [...prev, userMessage]);
    const currentMessage = inputMessage.trim();
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetchWithRetry(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentMessage,
          session_id: sessionId
        })
      });

      const data = await response.json();

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        id: generateMessageId()
      };

      setChatMessages(prev => [...prev, assistantMessage]);
      setConnectionStatus('connected');
      
    } catch (error) {
      console.error('Error sending message:', error);
      setConnectionStatus('error');
      
      const errorMessage = {
        role: 'assistant',
        content: `I apologize, but I'm experiencing technical difficulties right now. This could be due to:

• High demand on our AI services
• Temporary network connectivity issues
• Server maintenance

Please try again in a few moments. In the meantime, you can explore the dashboard or portfolio features.`,
        timestamp: new Date(),
        id: generateMessageId(),
        isError: true
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setChatMessages([]);
    addWelcomeMessage();
    localStorage.removeItem(SESSION_STORAGE_KEY);
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    localStorage.setItem(SESSION_STORAGE_KEY, newSessionId);
  };

  const refreshData = async () => {
    setError(null);
    await Promise.all([
      fetchMarketData(),
      fetchPortfolio('user123')
    ]);
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(num);
  };

  const formatPercentage = (value) => {
    const isPositive = value.startsWith('+');
    const isNegative = value.startsWith('-');
    const colorClass = isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-600';
    return <span className={colorClass}>{value}</span>;
  };

  const ConnectionStatus = () => {
    if (connectionStatus === 'connected') return null;
    
    return (
      <div className={`fixed top-4 right-4 px-4 py-2 rounded-lg text-white text-sm z-50 ${
        connectionStatus === 'loading' ? 'bg-blue-500' : 
        connectionStatus === 'error' ? 'bg-red-500' : 'bg-gray-500'
      }`}>
        {connectionStatus === 'loading' && '🔄 Loading...'}
        {connectionStatus === 'error' && '⚠️ Connection Issues'}
      </div>
    );
  };

  const DashboardView = () => (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <span className="text-red-500 mr-2">⚠️</span>
            <p className="text-red-700">{error}</p>
            <button 
              onClick={refreshData}
              className="ml-auto bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600"
            >
              Retry
            </button>
          </div>
        </div>
      )}

      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-blue-900 via-blue-800 to-indigo-900 rounded-2xl p-8 text-white overflow-hidden">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <img 
          src="https://images.unsplash.com/photo-1516245834210-c4c142787335?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwzfHxmaW5hbmNpYWwlMjB0ZWNobm9sb2d5fGVufDB8fHx8MTc1MzcyMDUyMnww&ixlib=rb-4.1.0&q=85" 
          alt="Financial Technology" 
          className="absolute inset-0 w-full h-full object-cover opacity-30"
        />
        <div className="relative z-10">
          <h1 className="text-4xl font-bold mb-2">Welcome to FinanceBot Pro</h1>
          <p className="text-xl opacity-90 mb-6">Advanced AI-Powered Financial Advisory & Portfolio Management</p>
          <div className="flex space-x-4">
            <button 
              onClick={() => setCurrentView('advisor')}
              className="bg-white text-blue-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-200 transform hover:scale-105"
            >
              💬 Talk to AI Advisor
            </button>
            <button 
              onClick={refreshData}
              className="border border-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-900 transition-all duration-200"
            >
              📊 Refresh Data
            </button>
          </div>
        </div>
      </div>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Portfolio Overview</h2>
            <div className={`w-3 h-3 rounded-full ${connectionStatus === 'connected' ? 'bg-green-400' : 'bg-red-400'}`}></div>
          </div>
          {portfolio && (
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
                <div>
                  <p className="text-gray-600 font-medium">Total Portfolio Value</p>
                  <p className="text-3xl font-bold text-green-600">{formatNumber(portfolio.total_value)}</p>
                </div>
                <div className="text-right">
                  <p className="text-gray-600 font-medium">Total Return</p>
                  <p className="text-xl font-semibold">{formatPercentage(portfolio.performance.total_return)}</p>
                  <p className="text-sm text-gray-500">Daily: {formatPercentage(portfolio.performance.daily_change)}</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700 mb-3">Top Holdings</h3>
                {portfolio.assets.slice(0, 3).map((asset, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                    <div>
                      <p className="font-semibold text-lg">{asset.symbol}</p>
                      <p className="text-sm text-gray-600">{asset.shares} shares</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-lg">{formatNumber(asset.current_price)}</p>
                      <p className="text-sm">
                        {formatPercentage(`+${((asset.current_price - asset.avg_price) / asset.avg_price * 100).toFixed(1)}%`)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Market Overview */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-800">Market Overview</h2>
            <button 
              onClick={fetchMarketData}
              className="text-blue-500 hover:text-blue-700 text-sm font-medium"
            >
              🔄 Refresh
            </button>
          </div>
          <div className="space-y-3">
            {Object.entries(marketData).slice(0, 6).map(([symbol, data]) => (
              <div key={symbol} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                <div>
                  <p className="font-semibold text-lg">{symbol}</p>
                  <p className="text-xl font-bold">{formatNumber(data.price)}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{formatPercentage(data.change)}</p>
                  <p className="text-sm">{formatPercentage(data.change_percent)}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div 
          onClick={() => setCurrentView('advisor')}
          className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
        >
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl">💡</span>
          </div>
          <h3 className="font-semibold text-gray-800 mb-2">Investment Ideas</h3>
          <p className="text-gray-600 text-sm">Get AI-powered investment recommendations tailored to your goals</p>
        </div>
        
        <div 
          onClick={() => setCurrentView('advisor')}
          className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
        >
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl">📊</span>
          </div>
          <h3 className="font-semibold text-gray-800 mb-2">Portfolio Analysis</h3>
          <p className="text-gray-600 text-sm">Deep dive analysis of your portfolio performance and optimization</p>
        </div>
        
        <div 
          onClick={() => setCurrentView('advisor')}
          className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-all duration-300 cursor-pointer transform hover:-translate-y-1"
        >
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl">🎯</span>
          </div>
          <h3 className="font-semibold text-gray-800 mb-2">Risk Assessment</h3>
          <p className="text-gray-600 text-sm">Evaluate and optimize your investment risk profile</p>
        </div>
      </div>
    </div>
  );

  const AdvisorView = () => (
    <div className="bg-white rounded-xl shadow-lg h-full flex flex-col">
      {/* Chat Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold">🤖</span>
              </div>
              <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${
                connectionStatus === 'connected' ? 'bg-green-400' : 
                connectionStatus === 'loading' ? 'bg-yellow-400' : 'bg-red-400'
              }`}></div>
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">AI Financial Advisor</h2>
              <p className="text-sm text-gray-600">Powered by NVIDIA Palmyra Financial AI</p>
            </div>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={clearChat}
              className="text-gray-500 hover:text-gray-700 px-3 py-1 rounded text-sm"
              title="Clear Chat"
            >
              🗑️ Clear
            </button>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatMessages.map((message, index) => (
          <div key={message.id || index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl p-4 rounded-2xl ${
              message.role === 'user' 
                ? 'bg-blue-500 text-white' 
                : message.isError 
                  ? 'bg-red-50 text-red-800 border border-red-200'
                  : 'bg-gray-100 text-gray-800'
            }`}>
              <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
              <div className={`text-xs mt-2 ${
                message.role === 'user' ? 'text-blue-100' : 
                message.isError ? 'text-red-500' : 'text-gray-500'
              }`}>
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-4 rounded-2xl max-w-xs">
              <p className="text-sm text-gray-600 mb-2">AI is thinking...</p>
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Chat Input */}
      <div className="border-t border-gray-200 p-4">
        {connectionStatus === 'error' && (
          <div className="mb-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
            ⚠️ Connection issues detected. Messages may be delayed.
          </div>
        )}
        <div className="flex space-x-3">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about investments, portfolio strategies, market analysis, risk management..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none transition-all duration-200"
            rows="2"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 active:scale-95"
          >
            {isLoading ? '⏳' : '📤'} Send
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          Press Enter to send • Shift+Enter for new line
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <ConnectionStatus />
      
      {/* Navigation */}
      <nav className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-blue-600">
                💼 FinanceBot Pro
                <span className="text-xs text-gray-500 ml-2">v1.0</span>
              </div>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-4 py-2 rounded-lg transition-all duration-200 ${
                  currentView === 'dashboard' 
                    ? 'bg-blue-500 text-white shadow-md' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                }`}
              >
                📊 Dashboard
              </button>
              <button
                onClick={() => setCurrentView('advisor')}
                className={`px-4 py-2 rounded-lg transition-all duration-200 ${
                  currentView === 'advisor' 
                    ? 'bg-blue-500 text-white shadow-md' 
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                }`}
              >
                🤖 AI Advisor
              </button>
            </div>
            
            <div className="flex items-center space-x-3">
              <span className="text-gray-700 hidden sm:block">Hello, {userName}</span>
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold cursor-pointer hover:bg-blue-600 transition-colors">
                {userName.charAt(0)}
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentView === 'dashboard' ? (
          <DashboardView />
        ) : (
          <div className="h-[calc(100vh-12rem)]">
            <AdvisorView />
          </div>
        )}
      </main>
    </div>
  );
}

export default App;