#!/usr/bin/env python3
"""
Test non-AI endpoints to verify backend functionality
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
print(f"Testing backend endpoints at: {BASE_URL}")

def test_health_check():
    """Test basic health check"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data}")
            return True
        else:
            print(f"❌ Health Check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Check error: {e}")
    return False

def test_market_data():
    """Test market data endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/market-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                market_data = data["data"]
                symbols = list(market_data.keys())[:5]
                print(f"✅ Market Data: Found {len(market_data)} symbols: {symbols}")
                return True
            else:
                print(f"❌ Market Data: Invalid response format")
        else:
            print(f"❌ Market Data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market Data error: {e}")
    return False

def test_user_profile():
    """Test user profile creation and retrieval"""
    try:
        user_id = f"test_user_{int(time.time())}"
        
        # Create profile
        profile_data = {
            "user_id": user_id,
            "name": "Test User",
            "email": "test@example.com",
            "investment_goals": "Long-term growth",
            "risk_tolerance": "moderate",
            "investment_amount": 10000.0
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/user/profile",
            json=profile_data,
            timeout=10
        )
        
        if create_response.status_code == 200:
            # Retrieve profile
            get_response = requests.get(f"{BASE_URL}/api/user/profile/{user_id}", timeout=10)
            if get_response.status_code == 200:
                profile = get_response.json()
                if profile.get("status") == "success":
                    print(f"✅ User Profile: Created and retrieved successfully")
                    return True
                else:
                    print(f"❌ User Profile: Invalid retrieval response")
            else:
                print(f"❌ User Profile: Retrieval failed: {get_response.status_code}")
        else:
            print(f"❌ User Profile: Creation failed: {create_response.status_code}")
    except Exception as e:
        print(f"❌ User Profile error: {e}")
    return False

def test_portfolio():
    """Test portfolio creation and retrieval"""
    try:
        user_id = f"test_user_{int(time.time())}"
        
        # Create portfolio
        portfolio_data = {
            "user_id": user_id,
            "assets": [
                {"symbol": "AAPL", "shares": 10, "avg_price": 190.50},
                {"symbol": "GOOGL", "shares": 2, "avg_price": 2800.00}
            ],
            "total_value": 7505.0,
            "performance": {"total_return": "+2.5%", "daily_change": "+0.8%"}
        }
        
        create_response = requests.post(
            f"{BASE_URL}/api/portfolio",
            json=portfolio_data,
            timeout=10
        )
        
        if create_response.status_code == 200:
            # Retrieve portfolio
            get_response = requests.get(f"{BASE_URL}/api/portfolio/{user_id}", timeout=10)
            if get_response.status_code == 200:
                portfolio = get_response.json()
                if portfolio.get("status") == "success":
                    print(f"✅ Portfolio: Created and retrieved successfully")
                    return True
                else:
                    print(f"❌ Portfolio: Invalid retrieval response")
            else:
                print(f"❌ Portfolio: Retrieval failed: {get_response.status_code}")
        else:
            print(f"❌ Portfolio: Creation failed: {create_response.status_code}")
    except Exception as e:
        print(f"❌ Portfolio error: {e}")
    return False

if __name__ == "__main__":
    print("=" * 60)
    print("BACKEND FUNCTIONALITY TEST (NON-AI ENDPOINTS)")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_health_check),
        ("Market Data", test_market_data),
        ("User Profile", test_user_profile),
        ("Portfolio", test_portfolio),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        time.sleep(1)
    
    print(f"\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("=" * 60)