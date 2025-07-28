from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import openai
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime, timedelta
import logging
import numpy as np
import pandas as pd
from scipy.optimize import minimize
import yfinance as yf
import json

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

class OptimizationRequest(BaseModel):
    symbols: List[str]
    investment_amount: float
    risk_tolerance: str = "moderate"  # conservative, moderate, aggressive
    optimization_method: str = "sharpe"  # sharpe, min_volatility, max_return

class OptimizationResult(BaseModel):
    symbols: List[str]
    weights: List[float]
    expected_return: float
    volatility: float
    sharpe_ratio: float
    allocation: Dict[str, float]
    efficient_frontier: Optional[List[Dict]] = None

# Portfolio Optimization Engine
class PortfolioOptimizer:
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
    
    def get_historical_data(self, symbols: List[str], period: str = "1y") -> pd.DataFrame:
        """Fetch historical price data for given symbols"""
        try:
            data = yf.download(symbols, period=period, progress=False)['Adj Close']
            if len(symbols) == 1:
                data = data.to_frame(symbols[0])
            return data.dropna()
        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            # Return mock data if yfinance fails
            dates = pd.date_range(end=datetime.now(), periods=252, freq='D')
            np.random.seed(42)
            mock_data = {}
            for symbol in symbols:
                returns = np.random.normal(0.001, 0.02, 252)
                prices = [100]
                for ret in returns[1:]:
                    prices.append(prices[-1] * (1 + ret))
                mock_data[symbol] = prices
            return pd.DataFrame(mock_data, index=dates)
    
    def calculate_returns_and_cov(self, price_data: pd.DataFrame):
        """Calculate expected returns and covariance matrix"""
        returns = price_data.pct_change().dropna()
        mean_returns = returns.mean() * 252  # Annualized returns
        cov_matrix = returns.cov() * 252  # Annualized covariance
        return mean_returns, cov_matrix
    
    def portfolio_stats(self, weights: np.ndarray, mean_returns: pd.Series, cov_matrix: pd.DataFrame):
        """Calculate portfolio statistics"""
        portfolio_return = np.sum(mean_returns * weights)
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        return portfolio_return, portfolio_volatility, sharpe_ratio
    
    def negative_sharpe_ratio(self, weights: np.ndarray, mean_returns: pd.Series, cov_matrix: pd.DataFrame):
        """Objective function to minimize (negative Sharpe ratio)"""
        _, _, sharpe = self.portfolio_stats(weights, mean_returns, cov_matrix)
        return -sharpe
    
    def portfolio_volatility(self, weights: np.ndarray, mean_returns: pd.Series, cov_matrix: pd.DataFrame):
        """Calculate portfolio volatility"""
        _, volatility, _ = self.portfolio_stats(weights, mean_returns, cov_matrix)
        return volatility
    
    def negative_portfolio_return(self, weights: np.ndarray, mean_returns: pd.Series, cov_matrix: pd.DataFrame):
        """Negative portfolio return for maximization"""
        portfolio_return, _, _ = self.portfolio_stats(weights, mean_returns, cov_matrix)
        return -portfolio_return
    
    def optimize_portfolio(self, symbols: List[str], method: str = "sharpe", risk_tolerance: str = "moderate"):
        """Main optimization function"""
        try:
            # Get historical data
            price_data = self.get_historical_data(symbols)
            mean_returns, cov_matrix = self.calculate_returns_and_cov(price_data)
            
            n_assets = len(symbols)
            
            # Constraints and bounds
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})  # weights sum to 1
            
            # Risk tolerance bounds
            if risk_tolerance == "conservative":
                bounds = tuple((0.05, 0.4) for _ in range(n_assets))  # Max 40% in any asset
            elif risk_tolerance == "moderate":
                bounds = tuple((0.02, 0.6) for _ in range(n_assets))  # Max 60% in any asset
            else:  # aggressive
                bounds = tuple((0.01, 0.8) for _ in range(n_assets))  # Max 80% in any asset
            
            # Initial guess (equal weights)
            initial_guess = np.array([1/n_assets] * n_assets)
            
            # Choose objective function
            if method == "sharpe":
                objective = self.negative_sharpe_ratio
            elif method == "min_volatility":
                objective = self.portfolio_volatility
            else:  # max_return
                objective = self.negative_portfolio_return
            
            # Optimize
            result = minimize(
                objective,
                initial_guess,
                args=(mean_returns, cov_matrix),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if result.success:
                optimal_weights = result.x
                portfolio_return, portfolio_volatility, sharpe_ratio = self.portfolio_stats(
                    optimal_weights, mean_returns, cov_matrix
                )
                
                # Create allocation dictionary
                allocation = {symbol: float(weight) for symbol, weight in zip(symbols, optimal_weights)}
                
                return {
                    "symbols": symbols,
                    "weights": optimal_weights.tolist(),
                    "expected_return": float(portfolio_return),
                    "volatility": float(portfolio_volatility),
                    "sharpe_ratio": float(sharpe_ratio),
                    "allocation": allocation
                }
            else:
                raise Exception("Optimization failed to converge")
                
        except Exception as e:
            logger.error(f"Portfolio optimization error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")
    
    def generate_efficient_frontier(self, symbols: List[str], num_portfolios: int = 10):
        """Generate efficient frontier data points"""
        try:
            price_data = self.get_historical_data(symbols)
            mean_returns, cov_matrix = self.calculate_returns_and_cov(price_data)
            
            n_assets = len(symbols)
            constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            bounds = tuple((0.01, 0.7) for _ in range(n_assets))
            initial_guess = np.array([1/n_assets] * n_assets)
            
            # Find minimum volatility portfolio
            min_vol_result = minimize(
                self.portfolio_volatility,
                initial_guess,
                args=(mean_returns, cov_matrix),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            min_vol_return, min_vol_volatility, _ = self.portfolio_stats(
                min_vol_result.x, mean_returns, cov_matrix
            )
            
            # Find maximum return portfolio
            max_ret_result = minimize(
                self.negative_portfolio_return,
                initial_guess,
                args=(mean_returns, cov_matrix),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            max_ret_return, max_ret_volatility, _ = self.portfolio_stats(
                max_ret_result.x, mean_returns, cov_matrix
            )
            
            # Generate target returns between min and max
            target_returns = np.linspace(min_vol_return, max_ret_return, num_portfolios)
            efficient_frontier = []
            
            for target_return in target_returns:
                # Add return constraint
                constraints_with_return = [
                    {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                    {'type': 'eq', 'fun': lambda x: np.sum(mean_returns * x) - target_return}
                ]
                
                result = minimize(
                    self.portfolio_volatility,
                    initial_guess,
                    args=(mean_returns, cov_matrix),
                    method='SLSQP',
                    bounds=bounds,
                    constraints=constraints_with_return
                )
                
                if result.success:
                    portfolio_return, portfolio_volatility, sharpe_ratio = self.portfolio_stats(
                        result.x, mean_returns, cov_matrix
                    )
                    
                    efficient_frontier.append({
                        "return": float(portfolio_return),
                        "volatility": float(portfolio_volatility),
                        "sharpe_ratio": float(sharpe_ratio)
                    })
            
            return efficient_frontier
            
        except Exception as e:
            logger.error(f"Efficient frontier error: {str(e)}")
            return []

# Initialize optimizer
optimizer = PortfolioOptimizer()

# Enhanced mock market data with more realistic financial data
ENHANCED_MARKET_DATA = {
    "AAPL": {"price": 195.30, "change": "+2.45", "change_percent": "+1.27%", "beta": 1.29, "pe_ratio": 32.4},
    "GOOGL": {"price": 2875.20, "change": "-15.30", "change_percent": "-0.53%", "beta": 1.03, "pe_ratio": 28.1},
    "MSFT": {"price": 415.75, "change": "+3.20", "change_percent": "+0.78%", "beta": 0.91, "pe_ratio": 35.2},
    "TSLA": {"price": 242.65, "change": "+8.40", "change_percent": "+3.58%", "beta": 2.09, "pe_ratio": 76.8},
    "NVDA": {"price": 925.40, "change": "+12.80", "change_percent": "+1.40%", "beta": 1.65, "pe_ratio": 45.3},
    "AMZN": {"price": 3485.75, "change": "-8.25", "change_percent": "-0.24%", "beta": 1.33, "pe_ratio": 52.7},
    "META": {"price": 485.20, "change": "+6.10", "change_percent": "+1.27%", "beta": 1.18, "pe_ratio": 24.9},
    "SPY": {"price": 478.32, "change": "+1.85", "change_percent": "+0.39%", "beta": 1.00, "pe_ratio": 26.2},
    "QQQ": {"price": 425.88, "change": "+2.12", "change_percent": "+0.50%", "beta": 1.15, "pe_ratio": 30.1},
    "VTI": {"price": 285.94, "change": "+1.44", "change_percent": "+0.51%", "beta": 1.02, "pe_ratio": 25.8},
    "BTC": {"price": 67420.30, "change": "+1240.80", "change_percent": "+1.87%", "beta": 3.50, "pe_ratio": None},
    "ETH": {"price": 3825.40, "change": "+95.20", "change_percent": "+2.55%", "beta": 2.80, "pe_ratio": None}
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
        return {"status": "success", "data": ENHANCED_MARKET_DATA}
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

@app.post("/api/optimize-portfolio", response_model=OptimizationResult)
async def optimize_portfolio(request: OptimizationRequest):
    """Optimize portfolio allocation using Modern Portfolio Theory"""
    try:
        result = optimizer.optimize_portfolio(
            symbols=request.symbols,
            method=request.optimization_method,
            risk_tolerance=request.risk_tolerance
        )
        
        # Generate efficient frontier if requested
        if request.optimization_method == "sharpe":
            efficient_frontier = optimizer.generate_efficient_frontier(request.symbols)
            result["efficient_frontier"] = efficient_frontier
        
        return OptimizationResult(**result)
        
    except Exception as e:
        logger.error(f"Portfolio optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@app.get("/api/efficient-frontier/{symbols}")
async def get_efficient_frontier(symbols: str):
    """Generate efficient frontier for given symbols"""
    try:
        symbol_list = symbols.split(",")
        if len(symbol_list) < 2:
            raise HTTPException(status_code=400, detail="At least 2 symbols required")
        
        frontier_data = optimizer.generate_efficient_frontier(symbol_list, num_portfolios=20)
        
        return {
            "status": "success",
            "data": {
                "symbols": symbol_list,
                "efficient_frontier": frontier_data
            }
        }
        
    except Exception as e:
        logger.error(f"Efficient frontier error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Efficient frontier calculation failed: {str(e)}")

@app.get("/api/portfolio-analysis/{symbols}")
async def analyze_portfolio(symbols: str, weights: str = None):
    """Analyze portfolio performance and risk metrics"""
    try:
        symbol_list = symbols.split(",")
        
        if weights:
            weight_list = [float(w) for w in weights.split(",")]
            if len(weight_list) != len(symbol_list):
                raise HTTPException(status_code=400, detail="Number of weights must match number of symbols")
            if abs(sum(weight_list) - 1.0) > 0.01:
                raise HTTPException(status_code=400, detail="Weights must sum to 1.0")
        else:
            # Equal weights if not provided
            weight_list = [1.0 / len(symbol_list)] * len(symbol_list)
        
        # Get historical data and calculate metrics
        price_data = optimizer.get_historical_data(symbol_list)
        mean_returns, cov_matrix = optimizer.calculate_returns_and_cov(price_data)
        
        weights_array = np.array(weight_list)
        portfolio_return, portfolio_volatility, sharpe_ratio = optimizer.portfolio_stats(
            weights_array, mean_returns, cov_matrix
        )
        
        # Calculate individual asset metrics
        asset_metrics = []
        for i, symbol in enumerate(symbol_list):
            asset_return = mean_returns[symbol]
            asset_volatility = np.sqrt(cov_matrix.loc[symbol, symbol])
            asset_sharpe = (asset_return - optimizer.risk_free_rate) / asset_volatility
            
            asset_metrics.append({
                "symbol": symbol,
                "weight": weight_list[i],
                "expected_return": float(asset_return),
                "volatility": float(asset_volatility),
                "sharpe_ratio": float(asset_sharpe)
            })
        
        return {
            "status": "success",
            "data": {
                "portfolio_metrics": {
                    "expected_return": float(portfolio_return),
                    "volatility": float(portfolio_volatility),
                    "sharpe_ratio": float(sharpe_ratio),
                    "risk_free_rate": optimizer.risk_free_rate
                },
                "asset_metrics": asset_metrics,
                "correlation_matrix": cov_matrix.corr().to_dict()
            }
        }
        
    except Exception as e:
        logger.error(f"Portfolio analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Portfolio analysis failed: {str(e)}")

@app.get("/api/market-data/enhanced")
async def get_enhanced_market_data():
    """Get enhanced market data with additional metrics"""
    try:
        return {"status": "success", "data": ENHANCED_MARKET_DATA}
    except Exception as e:
        logger.error(f"Enhanced market data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Enhanced market data service error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)