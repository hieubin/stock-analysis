import os
import sys
import logging
from pathlib import Path
import yaml
import sqlite3
import pymongo
from pymongo import MongoClient

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.constants import MONGODB_COLLECTIONS, SQLITE_TABLES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load database configuration from YAML file."""
    config_path = project_root / 'config' / 'config.yaml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise

def setup_mongodb(config):
    """Initialize MongoDB database and collections."""
    try:
        # Connect to MongoDB
        client = MongoClient(
            host=config['mongodb']['host'],
            port=config['mongodb']['port']
        )
        
        # Create database
        db = client[config['mongodb']['database']]
        
        # Create collections
        for collection_name in MONGODB_COLLECTIONS.values():
            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                logger.info(f"Created MongoDB collection: {collection_name}")
        
        # Create indexes
        db[MONGODB_COLLECTIONS['RAW_DATA']].create_index([
            ('symbol', pymongo.ASCENDING),
            ('date', pymongo.DESCENDING)
        ])
        
        db[MONGODB_COLLECTIONS['PROCESSED_DATA']].create_index([
            ('symbol', pymongo.ASCENDING),
            ('date', pymongo.DESCENDING)
        ])
        
        logger.info("MongoDB setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up MongoDB: {e}")
        raise

def setup_sqlite(config):
    """Initialize SQLite database and tables."""
    try:
        # Create database directory if it doesn't exist
        db_path = Path(config['sqlite']['path'])
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create recommendations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            rank INTEGER NOT NULL,
            score REAL NOT NULL,
            rsi REAL,
            macd REAL,
            volume_change REAL,
            price_momentum REAL,
            volatility REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            rationale TEXT
        )
        ''')
        
        # Create stock_info table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_info (
            symbol TEXT PRIMARY KEY,
            company_name TEXT,
            sector TEXT,
            market_cap REAL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create technical_indicators table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS technical_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date DATE NOT NULL,
            rsi REAL,
            macd REAL,
            signal_line REAL,
            sma_short REAL,
            sma_medium REAL,
            sma_long REAL,
            bb_upper REAL,
            bb_middle REAL,
            bb_lower REAL,
            UNIQUE(symbol, date)
        )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recommendations_symbol ON recommendations(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recommendations_timestamp ON recommendations(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_technical_indicators_symbol_date ON technical_indicators(symbol, date)')
        
        conn.commit()
        conn.close()
        
        logger.info("SQLite setup completed successfully")
        
    except Exception as e:
        logger.error(f"Error setting up SQLite: {e}")
        raise

def main():
    """Main function to set up databases."""
    try:
        # Load configuration
        config = load_config()
        
        # Setup MongoDB
        setup_mongodb(config)
        
        # Setup SQLite
        setup_sqlite(config)
        
        logger.info("Database setup completed successfully")
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
