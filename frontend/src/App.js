import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [marketData, setMarketData] = useState({});
  const [portfolio, setPortfolio] = useState(null);
  const [userName, setUserName] = useState('Guest');
  const chatEndRef = useRef(null);

  // Initialize session and load data
  useEffect(() => {
    const initializeApp = async () => {
      const newSessionId = generateSessionId();
      setSessionId(newSessionId);
      
      // Load market data
      await fetchMarketData();
      
      // Load portfolio
      await fetchPortfolio('user123'); // Mock user ID
      
      // Add welcome message
      setChatMessages([{
        role: 'assistant',
        content: `👋 Hello! I'm your AI Financial Advisor. I'm powered by advanced financial AI and ready to help you with:

• **Investment Strategy** - Portfolio recommendations and asset allocation
• **Market Analysis** - Real-time insights and trend analysis  
• **Risk Management** - Personalized risk assessment and mitigation
• **Financial Planning** - Retirement, tax-efficient strategies, and wealth building

What would you like to discuss about your financial goals today?`,
        timestamp: new Date()
      }]);
    };
    
    initializeApp();
  }, []);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const generateSessionId = () => {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  };

  const fetchMarketData = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/market-data`);
      const data = await response.json();
      if (data.status === 'success') {
        setMarketData(data.data);
      }
    } catch (error) {
      console.error('Error fetching market data:', error);
    }
  };

  const fetchPortfolio = async (userId) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/portfolio/${userId}`);
      const data = await response.json();
      if (data.status === 'success') {
        setPortfolio(data.data);
      }
    } catch (error) {
      console.error('Error fetching portfolio:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();

      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date()
      };

      setChatMessages(prev => [...prev, assistantMessage]);
      
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(num);
  };

  const DashboardView = () => (
    <div className="space-y-6">
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
          <p className="text-xl opacity-90 mb-6">AI-Powered Financial Advisory & Portfolio Management</p>
          <div className="flex space-x-4">
            <button 
              onClick={() => setCurrentView('advisor')}
              className="bg-white text-blue-900 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
            >
              Talk to AI Advisor
            </button>
            <button className="border border-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-900 transition-colors">
              View Portfolio
            </button>
          </div>
        </div>
      </div>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Portfolio Overview</h2>
          {portfolio && (
            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-green-50 rounded-lg">
                <div>
                  <p className="text-gray-600">Total Value</p>
                  <p className="text-3xl font-bold text-green-600">{formatNumber(portfolio.total_value)}</p>
                </div>
                <div className="text-right">
                  <p className="text-gray-600">Performance</p>
                  <p className="text-xl font-semibold text-green-600">{portfolio.performance.total_return}</p>
                </div>
              </div>
              
              <div className="space-y-2">
                <h3 className="font-semibold text-gray-700">Top Holdings</h3>
                {portfolio.assets.slice(0, 3).map((asset, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-semibold">{asset.symbol}</p>
                      <p className="text-sm text-gray-600">{asset.shares} shares</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">{formatNumber(asset.current_price)}</p>
                      <p className="text-sm text-green-600">+{((asset.current_price - asset.avg_price) / asset.avg_price * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Market Overview */}
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Market Overview</h2>
          <div className="space-y-3">
            {Object.entries(marketData).slice(0, 6).map(([symbol, data]) => (
              <div key={symbol} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-semibold">{symbol}</p>
                  <p className="text-2xl font-bold">{formatNumber(data.price)}</p>
                </div>
                <div className="text-right">
                  <p className={`font-semibold ${data.change.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {data.change}
                  </p>
                  <p className={`text-sm ${data.change_percent.startsWith('+') ? 'text-green-600' : 'text-red-600'}`}>
                    {data.change_percent}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl">💡</span>
          </div>
          <h3 className="font-semibold text-gray-800 mb-2">Investment Ideas</h3>
          <p className="text-gray-600">Get AI-powered investment recommendations</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl">📊</span>
          </div>
          <h3 className="font-semibold text-gray-800 mb-2">Portfolio Analysis</h3>
          <p className="text-gray-600">Deep dive into your portfolio performance</p>
        </div>
        
        <div className="bg-white rounded-xl shadow-lg p-6 text-center hover:shadow-xl transition-shadow cursor-pointer">
          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-2xl">🎯</span>
          </div>
          <h3 className="font-semibold text-gray-800 mb-2">Risk Assessment</h3>
          <p className="text-gray-600">Evaluate and optimize your risk profile</p>
        </div>
      </div>
    </div>
  );

  const AdvisorView = () => (
    <div className="bg-white rounded-xl shadow-lg h-full flex flex-col">
      {/* Chat Header */}
      <div className="border-b border-gray-200 p-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
            <span className="text-white font-bold">🤖</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-800">AI Financial Advisor</h2>
            <p className="text-sm text-gray-600">Powered by Llama 3.3 Nemotron Super 49B</p>
          </div>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {chatMessages.map((message, index) => (
          <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-3xl p-4 rounded-2xl ${
              message.role === 'user' 
                ? 'bg-blue-500 text-white' 
                : 'bg-gray-100 text-gray-800'
            }`}>
              <div className="whitespace-pre-wrap">{message.content}</div>
              <div className={`text-xs mt-2 ${message.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 p-4 rounded-2xl">
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
        <div className="flex space-x-3">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about investments, portfolio strategies, market analysis..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows="2"
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputMessage.trim()}
            className="bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="text-2xl font-bold text-blue-600">💼 FinanceBot Pro</div>
            </div>
            
            <div className="flex space-x-4">
              <button
                onClick={() => setCurrentView('dashboard')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentView === 'dashboard' 
                    ? 'bg-blue-500 text-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentView('advisor')}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentView === 'advisor' 
                    ? 'bg-blue-500 text-white' 
                    : 'text-gray-600 hover:bg-gray-100'
                }`}
              >
                AI Advisor
              </button>
            </div>
            
            <div className="flex items-center space-x-3">
              <span className="text-gray-700">Hello, {userName}</span>
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
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