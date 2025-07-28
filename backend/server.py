from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import openai
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FinanceBot Pro API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.financebot_pro

# Initialize OpenAI client for NVIDIA API
openai_client = openai.OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    investment_goals: Optional[str] = None
    risk_tolerance: Optional[str] = "moderate"
    investment_amount: Optional[float] = 0

class Portfolio(BaseModel):
    user_id: str
    assets: List[dict] = []
    total_value: float = 0
    performance: dict = {}

# Mock market data for demonstration
MOCK_MARKET_DATA = {
    "AAPL": {"price": 195.30, "change": "+2.45", "change_percent": "+1.27%"},
    "GOOGL": {"price": 2875.20, "change": "-15.30", "change_percent": "-0.53%"},
    "MSFT": {"price": 415.75, "change": "+3.20", "change_percent": "+0.78%"},
    "TSLA": {"price": 242.65, "change": "+8.40", "change_percent": "+3.58%"},
    "NVDA": {"price": 925.40, "change": "+12.80", "change_percent": "+1.40%"},
    "AMZN": {"price": 3485.75, "change": "-8.25", "change_percent": "-0.24%"},
    "META": {"price": 485.20, "change": "+6.10", "change_percent": "+1.27%"},
    "BTC": {"price": 67420.30, "change": "+1240.80", "change_percent": "+1.87%"},
    "ETH": {"price": 3825.40, "change": "+95.20", "change_percent": "+2.55%"}
}

@app.get("/")
async def root():
    return {"message": "FinanceBot Pro API is running"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_advisor(chat_request: ChatMessage):
    try:
        session_id = chat_request.session_id or str(uuid.uuid4())
        
        # Get chat history for context
        chat_history = await db.chat_history.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).limit(10).to_list(length=None)
        
        # Build conversation context
        messages = [
            {
                "role": "system", 
                "content": """You are FinanceBot Pro, an expert AI financial advisor. You provide personalized investment advice, portfolio recommendations, and financial planning guidance. You have deep knowledge of:

- Investment strategies and portfolio optimization
- Risk management and asset allocation
- Market analysis and trends
- Tax-efficient investing
- Retirement planning and wealth building
- Various asset classes (stocks, bonds, ETFs, crypto, etc.)

Always provide practical, actionable advice tailored to the user's situation. Be professional yet approachable. If asked about specific stocks or investments, provide balanced analysis considering both opportunities and risks."""
            }
        ]
        
        # Add recent chat history
        for msg in chat_history[-6:]:  # Last 6 messages for context
            messages.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
        
        # Add current message
        messages.append({"role": "user", "content": chat_request.message})
        
        # Call NVIDIA API with Llama 3.3 Nemotron model
        completion = openai_client.chat.completions.create(
            model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
            messages=messages,
            temperature=0.6,
            top_p=0.95,
            max_tokens=65536,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        response_text = completion.choices[0].message.content
        
        # Save conversation to database
        await db.chat_history.insert_many([
            {
                "session_id": session_id,
                "role": "user",
                "content": chat_request.message,
                "timestamp": datetime.utcnow()
            },
            {
                "session_id": session_id,
                "role": "assistant", 
                "content": response_text,
                "timestamp": datetime.utcnow()
            }
        ])
        
        return ChatResponse(response=response_text, session_id=session_id)
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@app.get("/api/market-data")
async def get_market_data():
    try:
        return {"status": "success", "data": MOCK_MARKET_DATA}
    except Exception as e:
        logger.error(f"Market data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Market data service error")

@app.post("/api/user/profile")
async def create_user_profile(profile: UserProfile):
    try:
        profile_dict = profile.dict()
        profile_dict["created_at"] = datetime.utcnow()
        
        await db.user_profiles.insert_one(profile_dict)
        return {"status": "success", "message": "Profile created successfully"}
    except Exception as e:
        logger.error(f"Profile creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Profile creation failed")

@app.get("/api/user/profile/{user_id}")
async def get_user_profile(user_id: str):
    try:
        profile = await db.user_profiles.find_one({"user_id": user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Remove MongoDB ObjectId for JSON serialization
        profile.pop("_id", None)
        return {"status": "success", "data": profile}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Profile fetch failed")

@app.post("/api/portfolio")
async def create_portfolio(portfolio: Portfolio):
    try:
        portfolio_dict = portfolio.dict()
        portfolio_dict["created_at"] = datetime.utcnow()
        portfolio_dict["updated_at"] = datetime.utcnow()
        
        await db.portfolios.insert_one(portfolio_dict)
        return {"status": "success", "message": "Portfolio created successfully"}
    except Exception as e:
        logger.error(f"Portfolio creation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Portfolio creation failed")

@app.get("/api/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    try:
        portfolio = await db.portfolios.find_one({"user_id": user_id})
        if not portfolio:
            # Create empty portfolio if none exists
            empty_portfolio = {
                "user_id": user_id,
                "assets": [
                    {"symbol": "AAPL", "shares": 10, "avg_price": 190.50, "current_price": 195.30},
                    {"symbol": "GOOGL", "shares": 2, "avg_price": 2800.00, "current_price": 2875.20},
                    {"symbol": "MSFT", "shares": 5, "avg_price": 400.00, "current_price": 415.75}
                ],
                "total_value": 8727.25,
                "performance": {"total_return": "+5.2%", "daily_change": "+1.1%"},
                "created_at": datetime.utcnow()
            }
            await db.portfolios.insert_one(empty_portfolio)
            portfolio = empty_portfolio
        
        # Remove MongoDB ObjectId for JSON serialization
        portfolio.pop("_id", None)
        return {"status": "success", "data": portfolio}
    except Exception as e:
        logger.error(f"Portfolio fetch error: {str(e)}")
        raise HTTPException(status_code=500, detail="Portfolio fetch failed")

@app.get("/api/chat-history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        messages = await db.chat_history.find(
            {"session_id": session_id}
        ).sort("timestamp", 1).to_list(length=None)
        
        # Clean up messages for frontend
        cleaned_messages = []
        for msg in messages:
            cleaned_messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            })
        
        return {"status": "success", "data": cleaned_messages}
    except Exception as e:
        logger.error(f"Chat history error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat history fetch failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)