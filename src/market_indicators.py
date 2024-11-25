import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta

from .constants import TIME_PERIODS

logger = logging.getLogger(__name__)

class MarketIndicators:
    @staticmethod
    def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(data: pd.Series) -> tuple:
        """Calculate MACD (Moving Average Convergence Divergence)."""
        exp1 = data.ewm(span=12, adjust=False).mean()
        exp2 = data.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal

    @staticmethod
    def calculate_bollinger_bands(data: pd.Series, period: int = 20, std: int = 2) -> tuple:
        """Calculate Bollinger Bands."""
        sma = data.rolling(window=period).mean()
        rolling_std = data.rolling(window=period).std()
        upper_band = sma + (rolling_std * std)
        lower_band = sma - (rolling_std * std)
        return upper_band, sma, lower_band

    @staticmethod
    def calculate_moving_averages(data: pd.Series) -> Dict[str, pd.Series]:
        """Calculate various moving averages."""
        return {
            'SMA_short': data.rolling(window=TIME_PERIODS['SHORT_TERM']).mean(),
            'SMA_medium': data.rolling(window=TIME_PERIODS['MEDIUM_TERM']).mean(),
            'SMA_long': data.rolling(window=TIME_PERIODS['LONG_TERM']).mean(),
            'EMA_short': data.ewm(span=TIME_PERIODS['SHORT_TERM']).mean(),
            'EMA_medium': data.ewm(span=TIME_PERIODS['MEDIUM_TERM']).mean()
        }

    @staticmethod
    def calculate_momentum(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate price momentum."""
        return data.diff(period)

    @staticmethod
    def calculate_volume_indicators(price: pd.Series, volume: pd.Series) -> Dict[str, pd.Series]:
        """Calculate volume-based indicators."""
        typical_price = price
        return {
            'OBV': (np.sign(price.diff()) * volume).cumsum(),
            'Volume_MA': volume.rolling(window=TIME_PERIODS['SHORT_TERM']).mean(),
            'PVT': (price.pct_change() * volume).cumsum()
        }

    @staticmethod
    def calculate_volatility(data: pd.Series, period: int = 14) -> pd.Series:
        """Calculate price volatility."""
        return data.pct_change().rolling(window=period).std()

    @staticmethod
    def calculate_stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, 
                                      k_period: int = 14, d_period: int = 3) -> tuple:
        """Calculate Stochastic Oscillator."""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=d_period).mean()
        
        return k, d

    @staticmethod
    def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators for a given dataframe."""
        try:
            # Price-based indicators
            df['RSI'] = self.calculate_rsi(df['close'])
            df['MACD'], df['Signal_Line'] = self.calculate_macd(df['close'])
            df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = self.calculate_bollinger_bands(df['close'])
            
            # Moving averages
            moving_averages = self.calculate_moving_averages(df['close'])
            for name, series in moving_averages.items():
                df[name] = series
            
            # Momentum and volatility
            df['Momentum'] = self.calculate_momentum(df['close'])
            df['Volatility'] = self.calculate_volatility(df['close'])
            
            # Volume indicators
            volume_indicators = self.calculate_volume_indicators(df['close'], df['volume'])
            for name, series in volume_indicators.items():
                df[name] = series
            
            # Stochastic Oscillator
            df['Stoch_K'], df['Stoch_D'] = self.calculate_stochastic_oscillator(
                df['high'], df['low'], df['close']
            )
            
            # ATR
            df['ATR'] = self.calculate_atr(df['high'], df['low'], df['close'])
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            raise

    def get_indicator_signals(self, df: pd.DataFrame) -> Dict[str, int]:
        """Generate trading signals based on technical indicators."""
        try:
            latest = df.iloc[-1]
            
            signals = {
                'RSI': 1 if 30 <= latest['RSI'] <= 70 else -1,
                'MACD': 1 if latest['MACD'] > latest['Signal_Line'] else -1,
                'BB': 1 if latest['close'] < latest['BB_Lower'] else (-1 if latest['close'] > latest['BB_Upper'] else 0),
                'MA': 1 if latest['SMA_short'] > latest['SMA_medium'] else -1,
                'Volume': 1 if latest['volume'] > latest['Volume_MA'] else -1,
                'Stochastic': 1 if latest['Stoch_K'] > latest['Stoch_D'] else -1
            }
            
            # Overall signal (simple average)
            signals['Overall'] = np.sign(sum(signals.values()))
            
            return signals
            
        except Exception as e:
            logger.error(f"Error generating indicator signals: {e}")
            raise
