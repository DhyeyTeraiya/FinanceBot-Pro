#!/usr/bin/env python3
"""
Single test for Palmyra model with rate limiting consideration
"""

import requests
import json
import uuid
import time

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
print(f"Testing single request at: {BASE_URL}")

def test_single_financial_question():
    """Test a single financial question with proper delay"""
    try:
        session_id = str(uuid.uuid4())
        chat_data = {
            "message": "What should I invest in? I have $5000 and I'm 25 years old.",
            "session_id": session_id
        }
        
        print("Testing single financial question (waiting for API response)...")
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=chat_data,
            timeout=60  # Longer timeout
        )
        
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "session_id" in data:
                ai_response = data["response"]
                print(f"\n✅ SUCCESS!")
                print(f"Response length: {len(ai_response)} characters")
                print(f"Session ID: {data['session_id']}")
                print(f"Response preview: {ai_response[:300]}...")
                
                # Check for financial keywords
                financial_terms = ["invest", "portfolio", "diversif", "risk", "return", "etf", "index", "emergency"]
                found_terms = [term for term in financial_terms if term.lower() in ai_response.lower()]
                print(f"Financial terms found: {found_terms}")
                
                return True
            else:
                print(f"❌ Invalid response format: {data}")
        else:
            print(f"❌ Status code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    return False

if __name__ == "__main__":
    print("=" * 50)
    print("SINGLE PALMYRA MODEL TEST")
    print("=" * 50)
    
    # Wait a bit to avoid rate limiting from previous tests
    print("Waiting 10 seconds to avoid rate limiting...")
    time.sleep(10)
    
    success = test_single_financial_question()
    
    if success:
        print("\n🎉 Palmyra model is working correctly!")
    else:
        print("\n⚠️  Palmyra model test failed")