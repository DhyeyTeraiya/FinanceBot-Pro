#!/usr/bin/env python3
"""
Test chat history and session management
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

def test_chat_history():
    """Test chat history retrieval"""
    try:
        # Use the session ID from the previous successful test
        session_id = "1420bdf8-d443-46a6-8de1-0f12135fb5d3"
        
        print(f"Testing chat history for session: {session_id}")
        response = requests.get(f"{BASE_URL}/api/chat-history/{session_id}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success" and "data" in data:
                messages = data["data"]
                print(f"✅ Chat History: Found {len(messages)} messages")
                
                for i, msg in enumerate(messages):
                    role = msg.get("role", "unknown")
                    content_preview = msg.get("content", "")[:100]
                    print(f"  {i+1}. {role}: {content_preview}...")
                
                return True
            else:
                print(f"❌ Chat History: Invalid response format")
        else:
            print(f"❌ Chat History failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat History error: {e}")
    return False

if __name__ == "__main__":
    print("=" * 50)
    print("CHAT HISTORY TEST")
    print("=" * 50)
    
    success = test_chat_history()
    
    if success:
        print("\n🎉 Chat history and session management working!")
    else:
        print("\n⚠️  Chat history test failed")