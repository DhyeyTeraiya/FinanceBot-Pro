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
    
    def test_session_management(self):
        """Test session management with follow-up chat"""
        try:
            # Send a follow-up message using the same session
            chat_data = {
                "message": "What about adding some tech stocks to that portfolio?",
                "session_id": self.session_id
            }
            
            print("Testing session management with follow-up message...")
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
                        self.log_result("Session Management", True, f"Follow-up response received with same session_id")
                        return True
                    else:
                        self.log_result("Session Management", False, f"Response too short: {ai_response}")
                else:
                    self.log_result("Session Management", False, f"Session ID mismatch or invalid response")
            else:
                self.log_result("Session Management", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Session Management", False, f"Error: {str(e)}")
        return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("FINANCEBOT PRO BACKEND API TESTING")
        print("=" * 60)
        
        # Test in logical order
        tests = [
            ("Health Check", self.test_health_check),
            ("Market Data", self.test_market_data),
            ("User Profile Creation", self.test_user_profile_creation),
            ("User Profile Retrieval", self.test_user_profile_retrieval),
            ("Portfolio Creation", self.test_portfolio_creation),
            ("Portfolio Retrieval", self.test_portfolio_retrieval),
            ("AI Chat Functionality", self.test_ai_chat_functionality),
            ("Chat History Persistence", self.test_chat_history_persistence),
            ("Session Management", self.test_session_management),
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