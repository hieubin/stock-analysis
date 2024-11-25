from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Database constants
MONGODB_COLLECTIONS = {
    'RAW_DATA': 'raw_stock_data',
    'PROCESSED_DATA': 'processed_stock_data'
}

SQLITE_TABLES = {
    'RECOMMENDATIONS': 'recommendations',
    'STOCK_INFO': 'stock_info',
    'TECHNICAL_INDICATORS': 'technical_indicators'
}

# Analysis constants
TECHNICAL_INDICATORS = [
    'RSI',  # Relative Strength Index
    'MACD',  # Moving Average Convergence Divergence
    'SMA',  # Simple Moving Average
    'EMA'   # Exponential Moving Average
]

TIME_PERIODS = {
    'SHORT_TERM': 14,
    'MEDIUM_TERM': 50,
    'LONG_TERM': 200
}

# Recommendation scoring weights
WEIGHTS = {
    'TECHNICAL_SCORE': 0.4,
    'VOLUME_SCORE': 0.2,
    'TREND_SCORE': 0.2,
    'VOLATILITY_SCORE': 0.2
}

# Web scraping constants
HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

# Error messages
ERROR_MESSAGES = {
    'DATA_NOT_FOUND': 'Requested data not found',
    'DATABASE_CONNECTION': 'Failed to connect to database',
    'INVALID_SYMBOL': 'Invalid stock symbol',
    'SCRAPING_ERROR': 'Error occurred while scraping data',
    'PROCESSING_ERROR': 'Error in data processing pipeline'
}
