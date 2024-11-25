import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.market_indicators import MarketIndicators

class TestMarketIndicators(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.indicators = MarketIndicators()
        
        # Create sample price data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.test_data = pd.DataFrame({
            'date': dates,
            'close': np.random.uniform(10, 20, len(dates)),
            'volume': np.random.randint(1000, 10000, len(dates))
        })

    def test_calculate_rsi(self):
        """Test RSI calculation."""
        rsi = self.indicators.calculate_rsi(self.test_data['close'])
        
        # Check RSI bounds
        self.assertTrue((rsi >= 0).all() and (rsi <= 100).all())
        
        # Test with constant prices
        constant_prices = pd.Series([10] * 100)
        constant_rsi = self.indicators.calculate_rsi(constant_prices)
        self.assertTrue((constant_rsi == 50).all())
        
        # Test with increasing prices
        increasing_prices = pd.Series(range(1, 101))
        increasing_rsi = self.indicators.calculate_rsi(increasing_prices)
        self.assertTrue((increasing_rsi > 50).all())

    def test_calculate_macd(self):
        """Test MACD calculation."""
        macd, signal = self.indicators.calculate_macd(self.test_data['close'])
        
        # Check MACD properties
        self.assertEqual(len(macd), len(self.test_data))
        self.assertEqual(len(signal), len(self.test_data))
        
        # Test with constant prices
        constant_prices = pd.Series([10] * 100)
        constant_macd, constant_signal = self.indicators.calculate_macd(constant_prices)
        self.assertTrue(np.abs(constant_macd).max() < 1e-10)

    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        upper, middle, lower = self.indicators.calculate_bollinger_bands(self.test_data['close'])
        
        # Check Bollinger Bands properties
        self.assertTrue((upper > middle).all())
        self.assertTrue((middle > lower).all())
        self.assertTrue((upper - lower > 0).all())
        
        # Test with constant prices
        constant_prices = pd.Series([10] * 100)
        upper_c, middle_c, lower_c = self.indicators.calculate_bollinger_bands(constant_prices)
        self.assertTrue(np.allclose(middle_c[20:], 10))  # After initial window

    def test_calculate_moving_averages(self):
        """Test moving averages calculation."""
        sma_short = self.indicators.calculate_sma(self.test_data['close'], window=10)
        sma_long = self.indicators.calculate_sma(self.test_data['close'], window=30)
        
        # Check moving average properties
        self.assertEqual(len(sma_short), len(self.test_data))
        self.assertEqual(len(sma_long), len(self.test_data))
        
        # Test with increasing prices
        increasing_prices = pd.Series(range(1, 101))
        sma = self.indicators.calculate_sma(increasing_prices, window=10)
        self.assertTrue((sma.diff()[10:] > 0).all())

    def test_calculate_momentum(self):
        """Test momentum calculation."""
        momentum = self.indicators.calculate_momentum(self.test_data['close'])
        
        # Check momentum properties
        self.assertEqual(len(momentum), len(self.test_data))
        
        # Test with constant prices
        constant_prices = pd.Series([10] * 100)
        constant_momentum = self.indicators.calculate_momentum(constant_prices)
        self.assertTrue((constant_momentum[1:] == 0).all())

    def test_calculate_volume_indicators(self):
        """Test volume indicator calculations."""
        volume_sma = self.indicators.calculate_volume_sma(self.test_data['volume'])
        volume_change = self.indicators.calculate_volume_change(self.test_data['volume'])
        
        # Check volume indicator properties
        self.assertEqual(len(volume_sma), len(self.test_data))
        self.assertEqual(len(volume_change), len(self.test_data))
        
        # Test with constant volume
        constant_volume = pd.Series([1000] * 100)
        constant_volume_change = self.indicators.calculate_volume_change(constant_volume)
        self.assertTrue((constant_volume_change[1:] == 0).all())

    def test_generate_signals(self):
        """Test trading signal generation."""
        signals = self.indicators.generate_signals(self.test_data)
        
        # Check signal properties
        self.assertTrue(set(signals['signal']).issubset({-1, 0, 1}))
        self.assertEqual(len(signals), len(self.test_data))
        
        # Test signal consistency
        self.assertTrue((signals['signal'].diff().abs() <= 2).all())

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with very short data
        short_data = self.test_data.iloc[:5]
        with self.assertRaises(Exception):
            self.indicators.calculate_macd(short_data['close'])
        
        # Test with NaN values
        nan_data = self.test_data.copy()
        nan_data.loc[10:20, 'close'] = np.nan
        with self.assertRaises(Exception):
            self.indicators.calculate_rsi(nan_data['close'])

    def test_indicator_relationships(self):
        """Test relationships between different indicators."""
        # Calculate all indicators
        rsi = self.indicators.calculate_rsi(self.test_data['close'])
        macd, signal = self.indicators.calculate_macd(self.test_data['close'])
        upper, middle, lower = self.indicators.calculate_bollinger_bands(self.test_data['close'])
        
        # Test RSI and MACD relationship during trends
        trend_mask = (macd > 0) & (macd.shift(1) > 0)
        self.assertTrue((rsi[trend_mask] > 40).all())
        
        # Test Bollinger Bands and price relationship
        self.assertTrue((upper >= self.test_data['close']).all())
        self.assertTrue((lower <= self.test_data['close']).all())

if __name__ == '__main__':
    unittest.main()
