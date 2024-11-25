import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

from .constants import (
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    TECHNICAL_INDICATORS,
    TIME_PERIODS
)

logger = logging.getLogger(__name__)

class StockDataProcessor:
    def __init__(self):
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None

    def load_data(self, symbol: str, start_date: Optional[str] = None) -> pd.DataFrame:
        """Load raw stock data from MongoDB or CSV files."""
        try:
            file_path = RAW_DATA_DIR / f"{symbol}_raw.csv"
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'])
            
            if start_date:
                start_date = pd.to_datetime(start_date)
                df = df[df['date'] >= start_date]
            
            df.sort_values('date', inplace=True)
            self.raw_data = df
            return df
        except Exception as e:
            logger.error(f"Error loading data for {symbol}: {e}")
            raise

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators for the stock data."""
        try:
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=TIME_PERIODS['SHORT_TERM']).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=TIME_PERIODS['SHORT_TERM']).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            # Moving Averages
            df['SMA_short'] = df['close'].rolling(window=TIME_PERIODS['SHORT_TERM']).mean()
            df['SMA_medium'] = df['close'].rolling(window=TIME_PERIODS['MEDIUM_TERM']).mean()
            df['SMA_long'] = df['close'].rolling(window=TIME_PERIODS['LONG_TERM']).mean()

            # EMA
            df['EMA_short'] = df['close'].ewm(span=TIME_PERIODS['SHORT_TERM']).mean()
            df['EMA_medium'] = df['close'].ewm(span=TIME_PERIODS['MEDIUM_TERM']).mean()

            # MACD
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

            # Volatility
            df['Daily_Return'] = df['close'].pct_change()
            df['Volatility'] = df['Daily_Return'].rolling(window=TIME_PERIODS['SHORT_TERM']).std()

            return df
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            raise

    def process_data(self, symbol: str, start_date: Optional[str] = None) -> pd.DataFrame:
        """Main data processing pipeline."""
        try:
            # Load data
            df = self.load_data(symbol, start_date)

            # Basic data cleaning
            df = df.dropna(subset=['close', 'volume'])
            df = df[df['volume'] > 0]

            # Calculate technical indicators
            df = self.calculate_technical_indicators(df)

            # Add derived features
            df['Price_Change'] = df['close'].pct_change()
            df['Volume_Change'] = df['volume'].pct_change()
            df['Average_Price'] = (df['high'] + df['low'] + df['close']) / 3
            
            # Trading signals
            df['SMA_Signal'] = np.where(df['SMA_short'] > df['SMA_medium'], 1, -1)
            df['MACD_Signal'] = np.where(df['MACD'] > df['Signal_Line'], 1, -1)
            
            # Save processed data
            output_path = PROCESSED_DATA_DIR / f"{symbol}_processed.csv"
            df.to_csv(output_path, index=False)
            
            self.processed_data = df
            return df

        except Exception as e:
            logger.error(f"Error in data processing pipeline for {symbol}: {e}")
            raise

    def get_market_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate market indicators for recommendation system."""
        try:
            latest = df.iloc[-1]
            return {
                'rsi': latest['RSI'],
                'macd': latest['MACD'],
                'macd_signal': latest['Signal_Line'],
                'volatility': latest['Volatility'],
                'sma_signal': latest['SMA_Signal'],
                'volume_change': latest['Volume_Change'],
                'price_momentum': df['Price_Change'].tail(TIME_PERIODS['SHORT_TERM']).mean()
            }
        except Exception as e:
            logger.error(f"Error calculating market indicators: {e}")
            raise

    def get_recommendation_score(self, symbol: str) -> float:
        """Calculate overall recommendation score based on technical indicators."""
        if self.processed_data is None:
            self.process_data(symbol)
            
        indicators = self.get_market_indicators(self.processed_data)
        
        # Score components
        rsi_score = 1.0 if 30 <= indicators['rsi'] <= 70 else 0.0
        macd_score = 1.0 if indicators['macd'] > indicators['macd_signal'] else 0.0
        trend_score = 1.0 if indicators['sma_signal'] > 0 else 0.0
        volume_score = 1.0 if indicators['volume_change'] > 0 else 0.0
        
        # Weighted average
        weights = [0.3, 0.3, 0.2, 0.2]
        scores = [rsi_score, macd_score, trend_score, volume_score]
        
        return sum(w * s for w, s in zip(weights, scores))
