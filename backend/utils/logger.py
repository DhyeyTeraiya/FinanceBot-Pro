"""
Enhanced logging utilities for FinanceBot Pro
"""
import logging
import sys
from datetime import datetime
from typing import Optional
from pythonjsonlogger import jsonlogger
from config import get_settings

settings = get_settings()


class ColoredFormatter(logging.Formatter):
    """Colored console formatter for better readability"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add color to levelname
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


def setup_logger(
    name: str,
    level: Optional[str] = None,
    use_json: bool = False
) -> logging.Logger:
    """
    Setup enhanced logger with optional JSON formatting
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Whether to use JSON formatting
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    
    if use_json:
        # JSON formatter for structured logging
        json_formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(json_formatter)
    else:
        # Colored formatter for console output
        colored_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(colored_formatter)
    
    logger.addHandler(console_handler)
    
    return logger


def log_api_request(
    logger: logging.Logger,
    method: str,
    endpoint: str,
    status_code: int,
    duration: float,
    user_id: Optional[str] = None
):
    """Log API request with structured information"""
    logger.info(
        "API Request",
        extra={
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2),
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def log_ai_interaction(
    logger: logging.Logger,
    session_id: str,
    message_length: int,
    response_length: int,
    model: str,
    duration: float,
    success: bool = True,
    error: Optional[str] = None
):
    """Log AI interaction with detailed metrics"""
    log_data = {
        "session_id": session_id,
        "message_length": message_length,
        "response_length": response_length,
        "model": model,
        "duration_ms": round(duration * 1000, 2),
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if error:
        log_data["error"] = error
    
    if success:
        logger.info("AI Interaction Success", extra=log_data)
    else:
        logger.error("AI Interaction Failed", extra=log_data)


def log_portfolio_optimization(
    logger: logging.Logger,
    symbols: list,
    method: str,
    risk_tolerance: str,
    duration: float,
    success: bool = True,
    error: Optional[str] = None
):
    """Log portfolio optimization with metrics"""
    log_data = {
        "symbols": symbols,
        "symbol_count": len(symbols),
        "optimization_method": method,
        "risk_tolerance": risk_tolerance,
        "duration_ms": round(duration * 1000, 2),
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if error:
        log_data["error"] = error
    
    if success:
        logger.info("Portfolio Optimization Success", extra=log_data)
    else:
        logger.error("Portfolio Optimization Failed", extra=log_data)


# Create application loggers
app_logger = setup_logger("financebot.app")
api_logger = setup_logger("financebot.api")
ai_logger = setup_logger("financebot.ai")
db_logger = setup_logger("financebot.database")
optimizer_logger = setup_logger("financebot.optimizer")