#!/usr/bin/env python3
"""
Focused test for Palmyra Financial Model API Configuration
Tests the specific issues mentioned by the user
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

print(f"Testing Palmyra Financial Model at: {BASE_URL}")

class PalmyraChatTester:
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
    
    def test_basic_hi_message(self):
        """Test basic 'hi' message to verify it doesn't respond with 'think>'"""
        try:
            chat_data = {
                "message": "hi",
                "session_id": self.session_id
            }
            
            print("Testing basic 'hi' message...")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data and "session_id" in data:
                    ai_response = data["response"]
                    print(f"Response received: {ai_response[:200]}...")
                    
                    # Check if response contains "think>" which was the reported issue
                    if "think>" in ai_response.lower():
                        self.log_result("Basic Hi Message", False, f"Response contains 'think>': {ai_response[:100]}")
                        return False
                    
                    # Check if response is a proper conversational response
                    if len(ai_response) > 10 and any(word in ai_response.lower() for word in ["hello", "hi", "help", "assist", "welcome", "greet"]):
                        self.log_result("Basic Hi Message", True, f"Proper greeting response: {len(ai_response)} chars")
                        return True
                    else:
                        self.log_result("Basic Hi Message", False, f"Response doesn't seem like proper greeting: {ai_response[:100]}")
                        return False
                else:
                    self.log_result("Basic Hi Message", False, f"Invalid response format: {data}")
            else:
                self.log_result("Basic Hi Message", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Basic Hi Message", False, f"Error: {str(e)}")
        return False
    
    def test_session_id_creation(self):
        """Test that session_id is created and managed correctly"""
        try:
            # Test without providing session_id
            chat_data = {
                "message": "Hello, I need help with investing"
            }
            
            print("Testing session ID creation...")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "session_id" in data:
                    new_session_id = data["session_id"]
                    if new_session_id and len(new_session_id) > 10:  # Should be a UUID
                        self.log_result("Session ID Creation", True, f"New session ID created: {new_session_id[:8]}...")
                        
                        # Test using the same session_id
                        follow_up_data = {
                            "message": "What about tech stocks?",
                            "session_id": new_session_id
                        }
                        
                        follow_up_response = requests.post(
                            f"{self.base_url}/api/chat",
                            json=follow_up_data,
                            timeout=30
                        )
                        
                        if follow_up_response.status_code == 200:
                            follow_up_json = follow_up_response.json()
                            if follow_up_json.get("session_id") == new_session_id:
                                self.log_result("Session ID Management", True, "Session ID maintained across requests")
                                return True
                            else:
                                self.log_result("Session ID Management", False, "Session ID not maintained")
                        else:
                            self.log_result("Session ID Management", False, f"Follow-up request failed: {follow_up_response.status_code}")
                    else:
                        self.log_result("Session ID Creation", False, f"Invalid session ID: {new_session_id}")
                else:
                    self.log_result("Session ID Creation", False, "No session_id in response")
            else:
                self.log_result("Session ID Creation", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Session ID Creation", False, f"Error: {str(e)}")
        return False
    
    def test_palmyra_model_integration(self):
        """Test that NVIDIA Palmyra model 'writer/palmyra-fin-70b-32k' is working"""
        try:
            chat_data = {
                "message": "Can you analyze the current market conditions and provide investment recommendations?",
                "session_id": self.session_id
            }
            
            print("Testing Palmyra model integration...")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=45  # Longer timeout for complex query
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    ai_response = data["response"]
                    print(f"Model response length: {len(ai_response)} characters")
                    
                    # Check for financial model characteristics
                    financial_indicators = [
                        "market", "investment", "portfolio", "risk", "return", 
                        "asset", "diversification", "allocation", "analysis", "recommend"
                    ]
                    
                    found_indicators = [ind for ind in financial_indicators if ind.lower() in ai_response.lower()]
                    indicator_percentage = len(found_indicators) / len(financial_indicators) * 100
                    
                    # Check response quality
                    if len(ai_response) > 200 and indicator_percentage > 30:
                        self.log_result("Palmyra Model Integration", True, 
                            f"Response: {len(ai_response)} chars, {indicator_percentage:.1f}% financial keywords")
                        return True
                    else:
                        self.log_result("Palmyra Model Integration", False, 
                            f"Poor response quality: {len(ai_response)} chars, {indicator_percentage:.1f}% financial keywords")
                else:
                    self.log_result("Palmyra Model Integration", False, "No response in data")
            else:
                self.log_result("Palmyra Model Integration", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Palmyra Model Integration", False, f"Error: {str(e)}")
        return False
    
    def test_financial_question_quality(self):
        """Test response quality for financial questions"""
        try:
            financial_question = "What should I invest in? I'm 30 years old with $10,000 to invest and moderate risk tolerance."
            
            chat_data = {
                "message": financial_question,
                "session_id": self.session_id
            }
            
            print("Testing financial question response quality...")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    ai_response = data["response"]
                    
                    # Detailed analysis of financial response
                    financial_terms = [
                        "diversif", "portfolio", "etf", "index", "bond", "stock", 
                        "risk", "return", "allocation", "emergency fund", "401k", 
                        "ira", "invest", "asset", "market", "dollar cost"
                    ]
                    
                    found_terms = [term for term in financial_terms if term.lower() in ai_response.lower()]
                    term_coverage = len(found_terms) / len(financial_terms) * 100
                    
                    # Check for structured advice
                    structure_indicators = ["1.", "2.", "first", "second", "consider", "recommend", "suggest"]
                    has_structure = any(ind in ai_response.lower() for ind in structure_indicators)
                    
                    print(f"Financial terms found: {found_terms}")
                    print(f"Term coverage: {term_coverage:.1f}%")
                    print(f"Has structure: {has_structure}")
                    
                    if len(ai_response) > 300 and term_coverage > 25 and has_structure:
                        self.log_result("Financial Question Quality", True, 
                            f"Comprehensive response: {len(ai_response)} chars, {term_coverage:.1f}% coverage, structured")
                        return True
                    else:
                        self.log_result("Financial Question Quality", False, 
                            f"Inadequate response: {len(ai_response)} chars, {term_coverage:.1f}% coverage, structured: {has_structure}")
                else:
                    self.log_result("Financial Question Quality", False, "No response in data")
            else:
                self.log_result("Financial Question Quality", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("Financial Question Quality", False, f"Error: {str(e)}")
        return False
    
    def test_error_handling(self):
        """Test error handling when API might fail"""
        try:
            # Test with empty message
            chat_data = {
                "message": "",
                "session_id": self.session_id
            }
            
            print("Testing error handling with empty message...")
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=chat_data,
                timeout=30
            )
            
            # Should either handle gracefully or return proper error
            if response.status_code == 200:
                data = response.json()
                if "response" in data:
                    ai_response = data["response"]
                    if len(ai_response) > 0:
                        self.log_result("Error Handling (Empty Message)", True, "Handled empty message gracefully")
                    else:
                        self.log_result("Error Handling (Empty Message)", False, "Empty response for empty message")
                else:
                    self.log_result("Error Handling (Empty Message)", False, "No response field")
            elif 400 <= response.status_code < 500:
                self.log_result("Error Handling (Empty Message)", True, f"Proper error response: {response.status_code}")
            else:
                self.log_result("Error Handling (Empty Message)", False, f"Unexpected status: {response.status_code}")
            
            # Test with malformed request
            try:
                malformed_response = requests.post(
                    f"{self.base_url}/api/chat",
                    json={"invalid": "data"},
                    timeout=30
                )
                
                if 400 <= malformed_response.status_code < 500:
                    self.log_result("Error Handling (Malformed Request)", True, f"Proper error for malformed request: {malformed_response.status_code}")
                    return True
                else:
                    self.log_result("Error Handling (Malformed Request)", False, f"Unexpected response to malformed request: {malformed_response.status_code}")
            except Exception as e:
                self.log_result("Error Handling (Malformed Request)", True, f"Request properly rejected: {str(e)}")
                return True
                
        except Exception as e:
            self.log_result("Error Handling", False, f"Error: {str(e)}")
        return False
    
    def run_focused_tests(self):
        """Run focused tests for Palmyra model issues"""
        print("=" * 70)
        print("PALMYRA FINANCIAL MODEL - FOCUSED TESTING")
        print("=" * 70)
        
        tests = [
            ("Basic Hi Message Test", self.test_basic_hi_message),
            ("Session ID Creation & Management", self.test_session_id_creation),
            ("Palmyra Model Integration", self.test_palmyra_model_integration),
            ("Financial Question Quality", self.test_financial_question_quality),
            ("Error Handling", self.test_error_handling),
        ]
        
        for test_name, test_func in tests:
            print(f"\n--- Running {test_name} ---")
            test_func()
            time.sleep(2)  # Pause between tests to avoid rate limiting
        
        # Summary
        print("\n" + "=" * 70)
        print("FOCUSED TEST SUMMARY")
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
        
        return self.results

if __name__ == "__main__":
    tester = PalmyraChatTester()
    results = tester.run_focused_tests()