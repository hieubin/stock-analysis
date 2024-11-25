import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.data_processing import StockDataProcessor

class TestStockDataProcessor(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.processor = StockDataProcessor()
        
        # Create sample stock data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': np.random.uniform(10, 20, len(dates)),
            'high': np.random.uniform(15, 25, len(dates)),
            'low': np.random.uniform(5, 15, len(dates)),
            'close': np.random.uniform(10, 20, len(dates)),
            'volume': np.random.randint(1000, 10000, len(dates))
        })
        
        # Ensure high is highest and low is lowest
        self.test_data['high'] = self.test_data[['open', 'close', 'high']].max(axis=1)
        self.test_data['low'] = self.test_data[['open', 'close', 'low']].min(axis=1)

    def test_calculate_technical_indicators(self):
        """Test technical indicator calculations."""
        df = self.processor.calculate_technical_indicators(self.test_data)
        
        # Check if indicators are calculated
        self.assertIn('RSI', df.columns)
        self.assertIn('MACD', df.columns)
        self.assertIn('Signal_Line', df.columns)
        self.assertIn('SMA_short', df.columns)
        self.assertIn('SMA_medium', df.columns)
        
        # Check RSI bounds
        self.assertTrue((df['RSI'] >= 0).all() and (df['RSI'] <= 100).all())
        
        # Check moving averages
        self.assertTrue((df['SMA_short'] >= df['low'].min()).all())
        self.assertTrue((df['SMA_short'] <= df['high'].max()).all())

    def test_process_data(self):
        """Test data processing pipeline."""
        self.processor.raw_data = self.test_data
        df = self.processor.process_data('TEST')
        
        # Check if all required columns are present
        required_columns = [
            'close', 'volume', 'RSI', 'MACD', 'Signal_Line',
            'SMA_short', 'SMA_medium', 'Price_Change', 'Volume_Change'
        ]
        for col in required_columns:
            self.assertIn(col, df.columns)
        
        # Check for NaN values
        self.assertFalse(df['close'].isna().any())
        self.assertFalse(df['volume'].isna().any())

    def test_get_market_indicators(self):
        """Test market indicator calculations."""
        df = self.processor.calculate_technical_indicators(self.test_data)
        indicators = self.processor.get_market_indicators(df)
        
        # Check if all indicators are present
        required_indicators = [
            'rsi', 'macd', 'macd_signal', 'volatility',
            'sma_signal', 'volume_change', 'price_momentum'
        ]
        for indicator in required_indicators:
            self.assertIn(indicator, indicators)
        
        # Check indicator values
        self.assertTrue(0 <= indicators['rsi'] <= 100)
        self.assertIsInstance(indicators['macd'], float)
        self.assertIsInstance(indicators['volatility'], float)

    def test_get_recommendation_score(self):
        """Test recommendation score calculation."""
        self.processor.raw_data = self.test_data
        self.processor.process_data('TEST')
        score = self.processor.get_recommendation_score('TEST')
        
        # Check score bounds
        self.assertTrue(0 <= score <= 1)
        self.assertIsInstance(score, float)

    def test_data_validation(self):
        """Test data validation and error handling."""
        # Test with missing required columns
        invalid_data = pd.DataFrame({
            'date': pd.date_range(start='2023-01-01', end='2023-01-10'),
            'close': np.random.random(10)  # Missing other required columns
        })
        
        with self.assertRaises(Exception):
            self.processor.calculate_technical_indicators(invalid_data)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with single day of data
        single_day = self.test_data.iloc[:1]
        with self.assertRaises(Exception):
            self.processor.calculate_technical_indicators(single_day)
        
        # Test with zero volume
        zero_volume = self.test_data.copy()
        zero_volume['volume'] = 0
        processed = self.processor.process_data('TEST')
        self.assertTrue(len(processed) < len(zero_volume))  # Should filter out zero volume

    def test_data_consistency(self):
        """Test data consistency and relationships."""
        df = self.processor.calculate_technical_indicators(self.test_data)
        
        # Test price-MA relationships
        self.assertTrue((df['SMA_short'].diff() >= -df['close'].std() * 10).all())
        self.assertTrue((df['SMA_medium'].diff() >= -df['close'].std() * 10).all())
        
        # Test MACD-Signal relationship
        macd_std = df['MACD'].std()
        self.assertTrue((df['MACD'] - df['Signal_Line']).abs().max() < macd_std * 10)

if __name__ == '__main__':
    unittest.main()
