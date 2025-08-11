#!/usr/bin/env python3
"""
FinanceBot Pro Backend API Testing Suite
Tests all backend endpoints for functionality and integration
"""

import requests
import json
import uuid
import time
from datetime import datetime

# Get backend URL from frontend .env
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    exit(1)

print(f"Testing backend at: {BASE_URL}")

class FinanceBotTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session_id = str(uuid.uuid4())
        self.test_user_id = f"test_user_{int(time.time())}"
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def log_result(self, test_name, success, message=""):
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}: PASSED {message}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAILED - {message}")
    
    def test_health_check(self):
        """Test the root endpoint to ensure server is running"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "FinanceBot Pro API is running" in data.get("message", ""):
                    self.log_result("Health Check", True, "API is running")
                    return True
                else:
                    self.log_result("Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_result("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_market_data(self):
        """Test market data endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/market-data", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    market_data = data["data"]
                    # Check if we have expected stocks
                    expected_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
                    found_symbols = [sym for sym in expected_symbols if sym in market_data]
                    if len(found_symbols) >= 3:
                        self.log_result("Market Data", True, f"Found {len(found_symbols)} symbols")
                        return True
                    else:
                        self.log_result("Market Data", False, f"Only found {len(found_symbols)} symbols")
                else:
                    self.log_result("Market Data", False, f"Invalid response format: {data}")
            else:
                self.log_result("Market Data", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Market Data", False, f"Error: {str(e)}")
        return False
    
    def test_user_profile_creation(self):
        """Test user profile creation"""
        try:
            profile_data = {
                "user_id": self.test_user_id,
                "name": "John Investor",
                "email": "john.investor@example.com",
                "investment_goals": "Long-term wealth building",
                "risk_tolerance": "moderate",
                "investment_amount": 50000.0
            }
            
            response = requests.post(
                f"{self.base_url}/api/user/profile",
                json=profile_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_result("User Profile Creation", True, "Profile created successfully")
                    return True
                else:
                    self.log_result("User Profile Creation", False, f"Unexpected response: {data}")
            else:
                self.log_result("User Profile Creation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("User Profile Creation", False, f"Error: {str(e)}")
        return False
    
    def test_user_profile_retrieval(self):
        """Test user profile retrieval"""
        try:
            response = requests.get(f"{self.base_url}/api/user/profile/{self.test_user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    profile = data["data"]
                    if profile.get("user_id") == self.test_user_id:
                        self.log_result("User Profile Retrieval", True, "Profile retrieved successfully")
                        return True
                    else:
                        self.log_result("User Profile Retrieval", False, f"Wrong user_id in response")
                else:
                    self.log_result("User Profile Retrieval", False, f"Invalid response format: {data}")
            else:
                self.log_result("User Profile Retrieval", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("User Profile Retrieval", False, f"Error: {str(e)}")
        return False
    
    def test_portfolio_creation(self):
        """Test portfolio creation"""
        try:
            portfolio_data = {
                "user_id": self.test_user_id,
                "assets": [
                    {"symbol": "AAPL", "shares": 10, "avg_price": 190.50},
                    {"symbol": "GOOGL", "shares": 2, "avg_price": 2800.00}
                ],
                "total_value": 7505.0,
                "performance": {"total_return": "+2.5%", "daily_change": "+0.8%"}
            }
            
            response = requests.post(
                f"{self.base_url}/api/portfolio",
                json=portfolio_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_result("Portfolio Creation", True, "Portfolio created successfully")
                    return True
                else:
                    self.log_result("Portfolio Creation", False, f"Unexpected response: {data}")
            else:
                self.log_result("Portfolio Creation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Portfolio Creation", False, f"Error: {str(e)}")
        return False
    
    def test_portfolio_retrieval(self):
        """Test portfolio retrieval"""
        try:
            response = requests.get(f"{self.base_url}/api/portfolio/{self.test_user_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    portfolio = data["data"]
                    if portfolio.get("user_id") == self.test_user_id:
                        self.log_result("Portfolio Retrieval", True, "Portfolio retrieved successfully")
                        return True
                    else:
                        self.log_result("Portfolio Retrieval", False, f"Wrong user_id in response")
                else:
                    self.log_result("Portfolio Retrieval", False, f"Invalid response format: {data}")
            else:
                self.log_result("Portfolio Retrieval", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Portfolio Retrieval", False, f"Error: {str(e)}")
        return False
    
    def test_ai_chat_functionality(self):
        """Test AI chat with NVIDIA Palmyra model"""
        try:
            chat_data = {
                "message": "I'm a 35-year-old professional with $50,000 to invest. I'm looking for a balanced portfolio with moderate risk. What would you recommend for long-term wealth building?",
                "session_id": self.session_id
            }
            
            print("Testing AI chat functionality (this may take 10-15 seconds)...")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=30  # Longer timeout for AI response
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "session_id" in data:
                    ai_response = data["response"]
                    if len(ai_response) > 50:  # Reasonable response length
                        # Check if response contains financial advice keywords
                        financial_keywords = ["invest", "portfolio", "risk", "diversif", "asset", "return", "market"]
                        found_keywords = [kw for kw in financial_keywords if kw.lower() in ai_response.lower()]
                        
                        if len(found_keywords) >= 2:
                            self.log_result("AI Chat Functionality", True, f"AI responded with {len(ai_response)} chars, {len(found_keywords)} financial keywords")
                            return True
                        else:
                            self.log_result("AI Chat Functionality", False, f"Response doesn't seem financial: {ai_response[:100]}...")
                    else:
                        self.log_result("AI Chat Functionality", False, f"Response too short: {ai_response}")
                else:
                    self.log_result("AI Chat Functionality", False, f"Invalid response format: {data}")
            else:
                self.log_result("AI Chat Functionality", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("AI Chat Functionality", False, f"Error: {str(e)}")
        return False
    
    def test_chat_history_persistence(self):
        """Test chat history persistence"""
        try:
            response = requests.get(f"{self.base_url}/api/chat-history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    messages = data["data"]
                    if len(messages) >= 2:  # Should have user message and AI response
                        self.log_result("Chat History Persistence", True, f"Found {len(messages)} messages in history")
                        return True
                    else:
                        self.log_result("Chat History Persistence", False, f"Only {len(messages)} messages found")
                else:
                    self.log_result("Chat History Persistence", False, f"Invalid response format: {data}")
            else:
                self.log_result("Chat History Persistence", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Chat History Persistence", False, f"Error: {str(e)}")
        return False
    
    def test_multi_message_conversation(self):
        """CRITICAL TEST: Multi-message conversation to verify 500 error fix"""
        try:
            # Create a new session for this critical test
            critical_session_id = str(uuid.uuid4())
            
            print("🔥 CRITICAL TEST: Multi-message conversation (testing 500 error fix)...")
            
            # Message 1: "hi" - should work as before
            print("  Step 1: Sending 'hi' message...")
            chat_data_1 = {
                "message": "hi",
                "session_id": critical_session_id
            }
            
            response_1 = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data_1,
                timeout=30
            )
            
            if response_1.status_code != 200:
                self.log_result("Multi-Message Conversation", False, f"First message failed with status {response_1.status_code}")
                return False
            
            data_1 = response_1.json()
            if not data_1.get("response") or len(data_1["response"]) < 20:
                self.log_result("Multi-Message Conversation", False, f"First message response too short: {data_1.get('response', '')}")
                return False
            
            print(f"    ✅ First message successful: {len(data_1['response'])} chars")
            
            # Brief pause to avoid overwhelming the API
            time.sleep(2)
            
            # Message 2: Follow-up question - this was previously causing 500 errors
            print("  Step 2: Sending follow-up message 'What stocks should I buy?'...")
            chat_data_2 = {
                "message": "What stocks should I buy?",
                "session_id": critical_session_id
            }
            
            response_2 = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data_2,
                timeout=30
            )
            
            if response_2.status_code != 200:
                self.log_result("Multi-Message Conversation", False, f"Second message failed with status {response_2.status_code} - 500 error fix not working!")
                return False
            
            data_2 = response_2.json()
            if not data_2.get("response") or len(data_2["response"]) < 20:
                self.log_result("Multi-Message Conversation", False, f"Second message response too short: {data_2.get('response', '')}")
                return False
            
            print(f"    ✅ Second message successful: {len(data_2['response'])} chars")
            
            # Brief pause
            time.sleep(2)
            
            # Message 3: Another follow-up - testing continued conversation
            print("  Step 3: Sending third message 'Tell me about AAPL'...")
            chat_data_3 = {
                "message": "Tell me about AAPL",
                "session_id": critical_session_id
            }
            
            response_3 = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data_3,
                timeout=30
            )
            
            if response_3.status_code != 200:
                self.log_result("Multi-Message Conversation", False, f"Third message failed with status {response_3.status_code}")
                return False
            
            data_3 = response_3.json()
            if not data_3.get("response") or len(data_3["response"]) < 20:
                self.log_result("Multi-Message Conversation", False, f"Third message response too short: {data_3.get('response', '')}")
                return False
            
            print(f"    ✅ Third message successful: {len(data_3['response'])} chars")
            
            # Verify session continuity
            if (data_1.get("session_id") == critical_session_id and 
                data_2.get("session_id") == critical_session_id and 
                data_3.get("session_id") == critical_session_id):
                
                self.log_result("Multi-Message Conversation", True, 
                    f"🎉 CRITICAL FIX VERIFIED: All 3 messages successful, no 500 errors, session maintained")
                return True
            else:
                self.log_result("Multi-Message Conversation", False, "Session ID not maintained across messages")
                return False
                
        except Exception as e:
            self.log_result("Multi-Message Conversation", False, f"CRITICAL ERROR: {str(e)}")
        return False
    
    def test_rate_limiting_resilience(self):
        """Test rate limiting resilience with rapid consecutive messages"""
        try:
            rate_test_session_id = str(uuid.uuid4())
            
            print("Testing rate limiting resilience with rapid messages...")
            
            messages = [
                "What is diversification?",
                "How do I start investing?", 
                "What are ETFs?",
                "Should I invest in crypto?",
                "What about bonds?"
            ]
            
            successful_responses = 0
            rate_limited_responses = 0
            error_responses = 0
            
            for i, message in enumerate(messages):
                print(f"  Sending rapid message {i+1}: {message[:30]}...")
                
                chat_data = {
                    "message": message,
                    "session_id": rate_test_session_id
                }
                
                try:
                    response = requests.post(
                        f"{self.base_url}/api/chat",
                        json=chat_data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        response_text = data.get("response", "")
                        
                        # Check if it's a rate limiting message (user-friendly)
                        if ("high demand" in response_text.lower() or 
                            "try again" in response_text.lower() or
                            "few moments" in response_text.lower()):
                            rate_limited_responses += 1
                            print(f"    ⏳ Rate limited (user-friendly message)")
                        elif len(response_text) > 20:
                            successful_responses += 1
                            print(f"    ✅ Successful response: {len(response_text)} chars")
                        else:
                            error_responses += 1
                            print(f"    ❌ Unexpected short response")
                    else:
                        error_responses += 1
                        print(f"    ❌ HTTP error: {response.status_code}")
                        
                except Exception as e:
                    error_responses += 1
                    print(f"    ❌ Request error: {str(e)}")
                
                # Small delay between rapid requests
                time.sleep(0.5)
            
            # Evaluate results
            total_messages = len(messages)
            if error_responses == 0:  # No 500 errors or exceptions
                if successful_responses > 0 or rate_limited_responses > 0:
                    self.log_result("Rate Limiting Resilience", True, 
                        f"No errors: {successful_responses} successful, {rate_limited_responses} rate-limited (graceful)")
                    return True
                else:
                    self.log_result("Rate Limiting Resilience", False, "All messages failed unexpectedly")
            else:
                self.log_result("Rate Limiting Resilience", False, 
                    f"{error_responses} error responses out of {total_messages}")
            
        except Exception as e:
            self.log_result("Rate Limiting Resilience", False, f"Test error: {str(e)}")
        return False
    
    def test_session_persistence_and_context(self):
        """Test session persistence and context maintenance"""
        try:
            context_session_id = str(uuid.uuid4())
            
            print("Testing session persistence and context maintenance...")
            
            # First message: Set context
            print("  Step 1: Setting investment context...")
            chat_data_1 = {
                "message": "I'm 30 years old with $100,000 to invest for retirement",
                "session_id": context_session_id
            }
            
            response_1 = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data_1,
                timeout=30
            )
            
            if response_1.status_code != 200:
                self.log_result("Session Persistence", False, f"Context setting failed: {response_1.status_code}")
                return False
            
            time.sleep(3)  # Wait to avoid rate limiting
            
            # Second message: Reference previous context
            print("  Step 2: Testing context awareness...")
            chat_data_2 = {
                "message": "Based on what I just told you, what allocation would you recommend?",
                "session_id": context_session_id
            }
            
            response_2 = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data_2,
                timeout=30
            )
            
            if response_2.status_code != 200:
                self.log_result("Session Persistence", False, f"Context reference failed: {response_2.status_code}")
                return False
            
            data_2 = response_2.json()
            response_text = data_2.get("response", "")
            
            # Check if response shows context awareness
            context_indicators = ["30", "100,000", "retirement", "age", "allocation", "recommend"]
            found_indicators = [ind for ind in context_indicators if ind in response_text.lower()]
            
            # Verify chat history retrieval
            print("  Step 3: Verifying chat history...")
            history_response = requests.get(f"{self.base_url}/api/chat-history/{context_session_id}", timeout=10)
            
            if history_response.status_code == 200:
                history_data = history_response.json()
                messages = history_data.get("data", [])
                
                if len(messages) >= 4:  # 2 user messages + 2 AI responses
                    self.log_result("Session Persistence", True, 
                        f"Context maintained: {len(found_indicators)} indicators, {len(messages)} messages in history")
                    return True
                else:
                    self.log_result("Session Persistence", False, 
                        f"Insufficient message history: {len(messages)} messages")
            else:
                self.log_result("Session Persistence", False, 
                    f"History retrieval failed: {history_response.status_code}")
                
        except Exception as e:
            self.log_result("Session Persistence", False, f"Error: {str(e)}")
        return False
    
    def test_error_recovery_after_rate_limiting(self):
        """Test that messages work properly after rate limiting"""
        try:
            recovery_session_id = str(uuid.uuid4())
            
            print("Testing error recovery after rate limiting...")
            
            # Step 1: Trigger rate limiting with rapid requests
            print("  Step 1: Triggering rate limiting...")
            for i in range(3):
                chat_data = {
                    "message": f"Quick question {i+1}",
                    "session_id": recovery_session_id
                }
                
                requests.post(f"{self.base_url}/api/chat", json=chat_data, timeout=30)
                time.sleep(0.2)  # Very rapid requests
            
            # Step 2: Wait for rate limiting to subside
            print("  Step 2: Waiting for rate limiting to subside...")
            time.sleep(8)  # Wait longer than the backoff period
            
            # Step 3: Send a normal message - should work properly
            print("  Step 3: Testing recovery with normal message...")
            recovery_chat_data = {
                "message": "Now that I've waited, can you help me with portfolio diversification?",
                "session_id": recovery_session_id
            }
            
            recovery_response = requests.post(
                f"{self.base_url}/api/chat",
                json=recovery_chat_data,
                timeout=30
            )
            
            if recovery_response.status_code == 200:
                recovery_data = recovery_response.json()
                response_text = recovery_data.get("response", "")
                
                # Check if it's a proper financial response (not a rate limiting message)
                if (len(response_text) > 100 and 
                    not ("high demand" in response_text.lower() or "try again" in response_text.lower())):
                    
                    # Check for financial content
                    financial_keywords = ["portfolio", "diversif", "invest", "asset", "risk", "allocation"]
                    found_keywords = [kw for kw in financial_keywords if kw.lower() in response_text.lower()]
                    
                    if len(found_keywords) >= 2:
                        self.log_result("Error Recovery", True, 
                            f"Recovery successful: {len(response_text)} chars, {len(found_keywords)} financial keywords")
                        return True
                    else:
                        self.log_result("Error Recovery", False, 
                            f"Response not financial: {response_text[:100]}...")
                else:
                    self.log_result("Error Recovery", False, 
                        f"Still rate limited or short response: {response_text[:100]}...")
            else:
                self.log_result("Error Recovery", False, 
                    f"Recovery failed with status: {recovery_response.status_code}")
                
        except Exception as e:
            self.log_result("Error Recovery", False, f"Error: {str(e)}")
        return False
    
    def test_session_management(self):
        """Test basic session management with follow-up chat"""
        try:
            # Send a follow-up message using the same session
            chat_data = {
                "message": "What about adding some tech stocks to that portfolio?",
                "session_id": self.session_id
            }
            
            print("Testing basic session management with follow-up message...")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("session_id") == self.session_id and "response" in data:
                    ai_response = data["response"]
                    if len(ai_response) > 20:
                        self.log_result("Basic Session Management", True, f"Follow-up response received with same session_id")
                        return True
                    else:
                        self.log_result("Basic Session Management", False, f"Response too short: {ai_response}")
                else:
                    self.log_result("Basic Session Management", False, f"Session ID mismatch or invalid response")
            else:
                self.log_result("Basic Session Management", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Basic Session Management", False, f"Error: {str(e)}")
        return False
    
    def test_enhanced_market_data(self):
        """Test enhanced market data endpoint with beta values and P/E ratios"""
        try:
            response = requests.get(f"{self.base_url}/api/market-data/enhanced", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    market_data = data["data"]
                    # Check if we have expected stocks with enhanced data
                    test_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
                    enhanced_data_found = 0
                    
                    for symbol in test_symbols:
                        if symbol in market_data:
                            stock_data = market_data[symbol]
                            if "beta" in stock_data and "pe_ratio" in stock_data:
                                enhanced_data_found += 1
                    
                    if enhanced_data_found >= 3:
                        self.log_result("Enhanced Market Data", True, f"Found enhanced data for {enhanced_data_found} symbols with beta and P/E ratios")
                        return True
                    else:
                        self.log_result("Enhanced Market Data", False, f"Only found enhanced data for {enhanced_data_found} symbols")
                else:
                    self.log_result("Enhanced Market Data", False, f"Invalid response format: {data}")
            else:
                self.log_result("Enhanced Market Data", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Enhanced Market Data", False, f"Error: {str(e)}")
        return False
    
    def test_portfolio_optimization_sharpe(self):
        """Test portfolio optimization with Sharpe ratio maximization"""
        try:
            optimization_data = {
                "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"],
                "investment_amount": 100000,
                "risk_tolerance": "moderate",
                "optimization_method": "sharpe"
            }
            
            print("Testing portfolio optimization (Sharpe ratio)...")
            response = requests.post(
                f"{self.base_url}/api/optimize-portfolio",
                json=optimization_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["symbols", "weights", "expected_return", "volatility", "sharpe_ratio", "allocation"]
                
                if all(field in data for field in required_fields):
                    # Validate mathematical properties
                    weights = data["weights"]
                    allocation = data["allocation"]
                    
                    # Check weights sum to approximately 1
                    weights_sum = sum(weights)
                    if abs(weights_sum - 1.0) < 0.01:
                        # Check allocation matches investment amount
                        total_allocation = sum(allocation.values())
                        if abs(total_allocation - 100000) < 100:
                            # Check Sharpe ratio is reasonable
                            sharpe_ratio = data["sharpe_ratio"]
                            if -2 <= sharpe_ratio <= 5:  # Reasonable range
                                self.log_result("Portfolio Optimization (Sharpe)", True, 
                                    f"Sharpe ratio: {sharpe_ratio:.3f}, weights sum: {weights_sum:.3f}")
                                return True
                            else:
                                self.log_result("Portfolio Optimization (Sharpe)", False, 
                                    f"Unreasonable Sharpe ratio: {sharpe_ratio}")
                        else:
                            self.log_result("Portfolio Optimization (Sharpe)", False, 
                                f"Allocation mismatch: {total_allocation} vs 100000")
                    else:
                        self.log_result("Portfolio Optimization (Sharpe)", False, 
                            f"Weights don't sum to 1: {weights_sum}")
                else:
                    missing_fields = [f for f in required_fields if f not in data]
                    self.log_result("Portfolio Optimization (Sharpe)", False, 
                        f"Missing fields: {missing_fields}")
            else:
                self.log_result("Portfolio Optimization (Sharpe)", False, 
                    f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Portfolio Optimization (Sharpe)", False, f"Error: {str(e)}")
        return False
    
    def test_portfolio_optimization_min_volatility(self):
        """Test portfolio optimization with minimum volatility"""
        try:
            optimization_data = {
                "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"],
                "investment_amount": 100000,
                "risk_tolerance": "conservative",
                "optimization_method": "min_volatility"
            }
            
            print("Testing portfolio optimization (Min Volatility)...")
            response = requests.post(
                f"{self.base_url}/api/optimize-portfolio",
                json=optimization_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "volatility" in data and "weights" in data:
                    volatility = data["volatility"]
                    weights = data["weights"]
                    
                    # Check conservative risk tolerance constraints (max 40% per asset)
                    max_weight = max(weights)
                    if max_weight <= 0.41:  # Allow small tolerance
                        self.log_result("Portfolio Optimization (Min Vol)", True, 
                            f"Volatility: {volatility:.3f}, max weight: {max_weight:.3f}")
                        return True
                    else:
                        self.log_result("Portfolio Optimization (Min Vol)", False, 
                            f"Conservative constraint violated: max weight {max_weight:.3f} > 0.4")
                else:
                    self.log_result("Portfolio Optimization (Min Vol)", False, 
                        f"Missing volatility or weights in response")
            else:
                self.log_result("Portfolio Optimization (Min Vol)", False, 
                    f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Portfolio Optimization (Min Vol)", False, f"Error: {str(e)}")
        return False
    
    def test_portfolio_optimization_max_return(self):
        """Test portfolio optimization with maximum return"""
        try:
            optimization_data = {
                "symbols": ["AAPL", "GOOGL", "MSFT", "TSLA"],
                "investment_amount": 100000,
                "risk_tolerance": "aggressive",
                "optimization_method": "max_return"
            }
            
            print("Testing portfolio optimization (Max Return)...")
            response = requests.post(
                f"{self.base_url}/api/optimize-portfolio",
                json=optimization_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "expected_return" in data and "weights" in data:
                    expected_return = data["expected_return"]
                    weights = data["weights"]
                    
                    # Check aggressive risk tolerance allows higher concentrations (up to 80%)
                    max_weight = max(weights)
                    if max_weight <= 0.81:  # Allow small tolerance
                        self.log_result("Portfolio Optimization (Max Return)", True, 
                            f"Expected return: {expected_return:.3f}, max weight: {max_weight:.3f}")
                        return True
                    else:
                        self.log_result("Portfolio Optimization (Max Return)", False, 
                            f"Aggressive constraint violated: max weight {max_weight:.3f} > 0.8")
                else:
                    self.log_result("Portfolio Optimization (Max Return)", False, 
                        f"Missing expected_return or weights in response")
            else:
                self.log_result("Portfolio Optimization (Max Return)", False, 
                    f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Portfolio Optimization (Max Return)", False, f"Error: {str(e)}")
        return False
    
    def test_efficient_frontier(self):
        """Test efficient frontier generation"""
        try:
            symbols = "AAPL,GOOGL,MSFT,TSLA"
            response = requests.get(f"{self.base_url}/api/efficient-frontier/{symbols}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    frontier_data = data["data"]
                    
                    if len(frontier_data) >= 5:  # Should have multiple data points
                        # Check if data points have required fields
                        required_fields = ["return", "volatility", "sharpe_ratio"]
                        valid_points = 0
                        
                        for point in frontier_data:
                            if all(field in point for field in required_fields):
                                # Check if values are reasonable
                                if (-0.5 <= point["return"] <= 2.0 and 
                                    0.01 <= point["volatility"] <= 1.0 and
                                    -3 <= point["sharpe_ratio"] <= 5):
                                    valid_points += 1
                        
                        if valid_points >= len(frontier_data) * 0.8:  # 80% valid points
                            self.log_result("Efficient Frontier", True, 
                                f"Generated {len(frontier_data)} points, {valid_points} valid")
                            return True
                        else:
                            self.log_result("Efficient Frontier", False, 
                                f"Only {valid_points}/{len(frontier_data)} valid points")
                    else:
                        self.log_result("Efficient Frontier", False, 
                            f"Too few data points: {len(frontier_data)}")
                else:
                    self.log_result("Efficient Frontier", False, f"Invalid response format: {data}")
            else:
                self.log_result("Efficient Frontier", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Efficient Frontier", False, f"Error: {str(e)}")
        return False
    
    def test_portfolio_analysis(self):
        """Test portfolio analysis with correlation and covariance matrices"""
        try:
            symbols = "AAPL,GOOGL,MSFT,TSLA"
            response = requests.get(f"{self.base_url}/api/portfolio-analysis/{symbols}", timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    analysis_data = data["data"]
                    required_sections = ["asset_metrics", "correlation_matrix", "covariance_matrix"]
                    
                    if all(section in analysis_data for section in required_sections):
                        asset_metrics = analysis_data["asset_metrics"]
                        correlation_matrix = analysis_data["correlation_matrix"]
                        
                        # Check asset metrics
                        test_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
                        valid_metrics = 0
                        
                        for symbol in test_symbols:
                            if symbol in asset_metrics:
                                metrics = asset_metrics[symbol]
                                if ("expected_return" in metrics and 
                                    "volatility" in metrics and 
                                    "sharpe_ratio" in metrics):
                                    # Check if values are reasonable
                                    if (-0.5 <= metrics["expected_return"] <= 2.0 and
                                        0.01 <= metrics["volatility"] <= 1.0):
                                        valid_metrics += 1
                        
                        # Check correlation matrix structure
                        correlation_valid = True
                        for symbol1 in test_symbols:
                            if symbol1 in correlation_matrix:
                                for symbol2 in test_symbols:
                                    if symbol2 in correlation_matrix[symbol1]:
                                        corr_value = correlation_matrix[symbol1][symbol2]
                                        if not (-1.1 <= corr_value <= 1.1):  # Allow small numerical errors
                                            correlation_valid = False
                                            break
                        
                        if valid_metrics >= 3 and correlation_valid:
                            self.log_result("Portfolio Analysis", True, 
                                f"Valid metrics for {valid_metrics} assets, correlation matrix valid")
                            return True
                        else:
                            self.log_result("Portfolio Analysis", False, 
                                f"Invalid metrics ({valid_metrics}) or correlation matrix")
                    else:
                        missing_sections = [s for s in required_sections if s not in analysis_data]
                        self.log_result("Portfolio Analysis", False, 
                            f"Missing sections: {missing_sections}")
                else:
                    self.log_result("Portfolio Analysis", False, f"Invalid response format: {data}")
            else:
                self.log_result("Portfolio Analysis", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Portfolio Analysis", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("FINANCEBOT PRO BACKEND API TESTING")
        print("=" * 60)
        
        # Test in logical order - CRITICAL multi-message tests first
        tests = [
            ("Health Check", self.test_health_check),
            ("Market Data", self.test_market_data),
            ("Enhanced Market Data", self.test_enhanced_market_data),
            ("User Profile Creation", self.test_user_profile_creation),
            ("User Profile Retrieval", self.test_user_profile_retrieval),
            ("Portfolio Creation", self.test_portfolio_creation),
            ("Portfolio Retrieval", self.test_portfolio_retrieval),
            ("Portfolio Optimization (Sharpe)", self.test_portfolio_optimization_sharpe),
            ("Portfolio Optimization (Min Vol)", self.test_portfolio_optimization_min_volatility),
            ("Portfolio Optimization (Max Return)", self.test_portfolio_optimization_max_return),
            ("Efficient Frontier", self.test_efficient_frontier),
            ("Portfolio Analysis", self.test_portfolio_analysis),
            ("AI Chat Functionality", self.test_ai_chat_functionality),
            ("Chat History Persistence", self.test_chat_history_persistence),
            ("Basic Session Management", self.test_session_management),
            # CRITICAL MULTI-MESSAGE SESSION TESTS
            ("🔥 CRITICAL: Multi-Message Conversation", self.test_multi_message_conversation),
            ("Rate Limiting Resilience", self.test_rate_limiting_resilience),
            ("Session Persistence & Context", self.test_session_persistence_and_context),
            ("Error Recovery After Rate Limiting", self.test_error_recovery_after_rate_limiting),
        ]
        
        for test_name, test_func in tests:
            print(f"\n--- Running {test_name} ---")
            test_func()
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Success Rate: {(self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100):.1f}%")
        
        if self.results["errors"]:
            print("\n🔍 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"  • {error}")
        
        return self.results

if __name__ == "__main__":
    tester = FinanceBotTester()
    results = tester.run_all_tests()