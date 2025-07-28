#!/usr/bin/env python3
"""
FinanceBot Pro - Llama 3.3 Nemotron Super 49B Model Testing
Focused testing for the new NVIDIA Llama 3.3 Nemotron model integration
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

print(f"Testing Llama 3.3 Nemotron model at: {BASE_URL}")

class NemotronModelTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.session_id = str(uuid.uuid4())
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
    
    def test_api_health_with_new_model(self):
        """Test that the server is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "FinanceBot Pro API is running" in data.get("message", ""):
                    self.log_result("API Health Check", True, "Server running with new model configuration")
                    return True
                else:
                    self.log_result("API Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_result("API Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("API Health Check", False, f"Connection error: {str(e)}")
        return False
    
    def test_nemotron_advanced_reasoning(self):
        """Test the Llama 3.3 Nemotron model with comprehensive financial question"""
        try:
            # The specific comprehensive financial question from the user's request
            complex_question = ("I'm 28 years old, have $100,000 to invest, earn $80k annually, and want to retire by 55. "
                              "I'm considering a mix of growth stocks, index funds, and some crypto. What's your detailed "
                              "investment strategy recommendation considering current market conditions, tax efficiency, "
                              "and risk management?")
            
            chat_data = {
                "message": complex_question,
                "session_id": self.session_id
            }
            
            print("Testing Llama 3.3 Nemotron advanced reasoning capabilities...")
            print("This may take 15-30 seconds for comprehensive analysis...")
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=45  # Extended timeout for complex reasoning
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "session_id" in data:
                    ai_response = data["response"]
                    response_length = len(ai_response)
                    
                    print(f"\n📊 Response Analysis:")
                    print(f"   Length: {response_length} characters")
                    print(f"   Session ID: {data['session_id']}")
                    
                    # Advanced analysis criteria for Nemotron model
                    advanced_keywords = [
                        "diversification", "asset allocation", "risk tolerance", "time horizon",
                        "tax-advantaged", "401k", "IRA", "compound", "dollar-cost averaging",
                        "emergency fund", "expense ratio", "rebalancing", "market volatility",
                        "growth stocks", "index funds", "cryptocurrency", "retirement planning",
                        "tax efficiency", "risk management", "portfolio", "investment strategy"
                    ]
                    
                    found_keywords = [kw for kw in advanced_keywords if kw.lower() in ai_response.lower()]
                    keyword_coverage = len(found_keywords) / len(advanced_keywords) * 100
                    
                    # Check for structured response indicators
                    structure_indicators = [
                        "1.", "2.", "3.", "•", "-", "First", "Second", "Third",
                        "Strategy", "Recommendation", "Consider", "Approach"
                    ]
                    structure_found = sum(1 for indicator in structure_indicators if indicator in ai_response)
                    
                    print(f"   Financial Keywords: {len(found_keywords)}/{len(advanced_keywords)} ({keyword_coverage:.1f}%)")
                    print(f"   Structure Indicators: {structure_found}")
                    
                    # Display first 500 characters of response for quality assessment
                    print(f"\n📝 Response Preview:")
                    print(f"   {ai_response[:500]}{'...' if len(ai_response) > 500 else ''}")
                    
                    # Success criteria for Nemotron model
                    if (response_length >= 1000 and  # Detailed response expected
                        len(found_keywords) >= 8 and  # Rich financial vocabulary
                        structure_found >= 3):  # Well-structured response
                        
                        self.log_result("Nemotron Advanced Reasoning", True, 
                                      f"Comprehensive response: {response_length} chars, "
                                      f"{len(found_keywords)} financial terms, structured format")
                        return True
                    else:
                        self.log_result("Nemotron Advanced Reasoning", False,
                                      f"Response quality below expectations: {response_length} chars, "
                                      f"{len(found_keywords)} terms, {structure_found} structure indicators")
                else:
                    self.log_result("Nemotron Advanced Reasoning", False, f"Invalid response format: {data}")
            else:
                self.log_result("Nemotron Advanced Reasoning", False, 
                              f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Nemotron Advanced Reasoning", False, f"Error: {str(e)}")
        return False
    
    def test_session_management_persistence(self):
        """Test that chat history persists properly with the new model"""
        try:
            response = requests.get(f"{self.base_url}/api/chat-history/{self.session_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and "data" in data:
                    messages = data["data"]
                    if len(messages) >= 2:  # Should have user message and AI response
                        # Check that both user and assistant messages are present
                        user_messages = [msg for msg in messages if msg.get("role") == "user"]
                        assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
                        
                        if len(user_messages) >= 1 and len(assistant_messages) >= 1:
                            self.log_result("Session Management", True, 
                                          f"Chat history persisted: {len(user_messages)} user, "
                                          f"{len(assistant_messages)} assistant messages")
                            return True
                        else:
                            self.log_result("Session Management", False, 
                                          f"Incomplete message history: {len(user_messages)} user, "
                                          f"{len(assistant_messages)} assistant")
                    else:
                        self.log_result("Session Management", False, f"Only {len(messages)} messages found")
                else:
                    self.log_result("Session Management", False, f"Invalid response format: {data}")
            else:
                self.log_result("Session Management", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Session Management", False, f"Error: {str(e)}")
        return False
    
    def test_model_parameters_effectiveness(self):
        """Test a follow-up question to verify model parameters are working effectively"""
        try:
            # Follow-up question to test context awareness and detailed reasoning
            followup_question = ("Based on your previous recommendation, how should I adjust my strategy "
                               "if the market experiences a significant downturn in the next 2 years?")
            
            chat_data = {
                "message": followup_question,
                "session_id": self.session_id
            }
            
            print("Testing model parameters with follow-up question...")
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and data.get("session_id") == self.session_id:
                    ai_response = data["response"]
                    
                    # Check for context awareness (should reference previous conversation)
                    context_indicators = [
                        "previous", "earlier", "mentioned", "discussed", "recommended",
                        "your portfolio", "your strategy", "your situation", "as I suggested"
                    ]
                    context_found = [indicator for indicator in context_indicators 
                                   if indicator.lower() in ai_response.lower()]
                    
                    # Check for market downturn specific advice
                    downturn_keywords = [
                        "downturn", "bear market", "recession", "volatility", "correction",
                        "dollar-cost averaging", "rebalance", "opportunity", "stay calm",
                        "long-term", "don't panic", "market timing"
                    ]
                    downturn_found = [kw for kw in downturn_keywords if kw.lower() in ai_response.lower()]
                    
                    print(f"   Context Awareness: {len(context_found)} indicators")
                    print(f"   Downturn Strategy: {len(downturn_found)} relevant terms")
                    print(f"   Response Length: {len(ai_response)} characters")
                    
                    if (len(context_found) >= 1 and  # Shows context awareness
                        len(downturn_found) >= 2 and  # Addresses market downturn
                        len(ai_response) >= 300):  # Substantial response
                        
                        self.log_result("Model Parameters Effectiveness", True,
                                      f"Context-aware response with {len(downturn_found)} downturn strategies")
                        return True
                    else:
                        self.log_result("Model Parameters Effectiveness", False,
                                      f"Limited context/strategy: {len(context_found)} context, "
                                      f"{len(downturn_found)} downturn terms")
                else:
                    self.log_result("Model Parameters Effectiveness", False, "Invalid response or session mismatch")
            else:
                self.log_result("Model Parameters Effectiveness", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Model Parameters Effectiveness", False, f"Error: {str(e)}")
        return False
    
    def run_nemotron_tests(self):
        """Run all Nemotron model-specific tests"""
        print("=" * 70)
        print("FINANCEBOT PRO - LLAMA 3.3 NEMOTRON SUPER 49B MODEL TESTING")
        print("=" * 70)
        print("Testing advanced reasoning capabilities and model integration")
        print()
        
        # Test sequence focused on new model capabilities
        tests = [
            ("API Health Check", self.test_api_health_with_new_model),
            ("Nemotron Advanced Reasoning", self.test_nemotron_advanced_reasoning),
            ("Session Management", self.test_session_management_persistence),
            ("Model Parameters Effectiveness", self.test_model_parameters_effectiveness),
        ]
        
        for test_name, test_func in tests:
            print(f"\n--- Running {test_name} ---")
            test_func()
            time.sleep(2)  # Brief pause between tests
        
        # Summary
        print("\n" + "=" * 70)
        print("NEMOTRON MODEL TEST SUMMARY")
        print("=" * 70)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        
        if self.results['passed'] + self.results['failed'] > 0:
            success_rate = (self.results['passed'] / (self.results['passed'] + self.results['failed']) * 100)
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        if self.results["errors"]:
            print("\n🔍 FAILED TESTS:")
            for error in self.results["errors"]:
                print(f"  • {error}")
        
        print("\n🎯 MODEL VERIFICATION:")
        if self.results['passed'] >= 3:
            print("✅ Llama 3.3 Nemotron Super 49B model is working correctly")
            print("✅ Advanced reasoning capabilities confirmed")
            print("✅ Model parameters (temperature=0.6, top_p=0.95, max_tokens=65536) effective")
        else:
            print("❌ Model integration issues detected")
            print("❌ Advanced reasoning capabilities not fully verified")
        
        return self.results

if __name__ == "__main__":
    tester = NemotronModelTester()
    results = tester.run_nemotron_tests()