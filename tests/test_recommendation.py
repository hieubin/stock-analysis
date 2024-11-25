import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.recommendation import StockRecommender

class TestStockRecommender(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.recommender = StockRecommender()
        
        # Create sample stock data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        num_stocks = 10
        
        # Generate test data for multiple stocks
        self.test_data = {}
        for i in range(num_stocks):
            stock_data = pd.DataFrame({
                'date': dates,
                'close': np.random.uniform(10, 20, len(dates)),
                'volume': np.random.randint(1000, 10000, len(dates)),
                'RSI': np.random.uniform(30, 70, len(dates)),
                'MACD': np.random.uniform(-1, 1, len(dates)),
                'Signal_Line': np.random.uniform(-1, 1, len(dates)),
                'SMA_short': np.random.uniform(10, 20, len(dates)),
                'SMA_medium': np.random.uniform(10, 20, len(dates))
            })
            stock_data.set_index('date', inplace=True)
            self.test_data[f'STOCK_{i+1}'] = stock_data

    def test_calculate_recommendation_score(self):
        """Test recommendation score calculation."""
        stock_data = self.test_data['STOCK_1']
        score = self.recommender.calculate_recommendation_score(stock_data)
        
        # Check score properties
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 1)
        
        # Test with extreme values
        extreme_data = stock_data.copy()
        extreme_data['RSI'] = 20  # Oversold
        extreme_data['MACD'] = 2  # Strong uptrend
        extreme_score = self.recommender.calculate_recommendation_score(extreme_data)
        self.assertGreater(extreme_score, score)

    def test_analyze_stock(self):
        """Test individual stock analysis."""
        analysis = self.recommender.analyze_stock(
            self.test_data['STOCK_1'],
            'STOCK_1'
        )
        
        # Check analysis results
        required_fields = [
            'symbol', 'score', 'rsi', 'macd',
            'volume_change', 'price_momentum', 'recommendation'
        ]
        for field in required_fields:
            self.assertIn(field, analysis)
        
        # Check recommendation format
        self.assertIsInstance(analysis['recommendation'], str)
        self.assertGreater(len(analysis['recommendation']), 0)

    def test_generate_recommendations(self):
        """Test recommendation generation for multiple stocks."""
        recommendations = self.recommender.generate_recommendations(self.test_data)
        
        # Check recommendations structure
        self.assertEqual(len(recommendations), len(self.test_data))
        self.assertTrue(all(isinstance(r, dict) for r in recommendations))
        
        # Check if recommendations are sorted by score
        scores = [r['score'] for r in recommendations]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_get_top_picks(self):
        """Test top stock picks selection."""
        num_picks = 5
        top_picks = self.recommender.get_top_picks(self.test_data, num_picks)
        
        # Check number of picks
        self.assertEqual(len(top_picks), num_picks)
        
        # Check if picks are sorted by score
        scores = [p['score'] for p in top_picks]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_generate_report(self):
        """Test recommendation report generation."""
        report = self.recommender.generate_report(self.test_data)
        
        # Check report structure
        required_sections = [
            'timestamp', 'summary', 'top_picks',
            'detailed_analysis', 'market_conditions'
        ]
        for section in required_sections:
            self.assertIn(section, report)
        
        # Check timestamp format
        self.assertIsInstance(
            datetime.strptime(report['timestamp'], '%Y-%m-%d %H:%M:%S'),
            datetime
        )

    def test_filter_stocks(self):
        """Test stock filtering based on criteria."""
        criteria = {
            'min_score': 0.7,
            'max_rsi': 70,
            'min_volume': 5000
        }
        
        filtered = self.recommender.filter_stocks(
            self.test_data,
            criteria
        )
        
        # Check filtering results
        self.assertIsInstance(filtered, dict)
        for symbol, data in filtered.items():
            latest_data = data.iloc[-1]
            self.assertGreater(latest_data['volume'], criteria['min_volume'])
            self.assertLess(latest_data['RSI'], criteria['max_rsi'])

    def test_calculate_sector_recommendations(self):
        """Test sector-based recommendations."""
        # Add sector information
        sectors = {
            'STOCK_1': 'Technology',
            'STOCK_2': 'Technology',
            'STOCK_3': 'Finance',
            'STOCK_4': 'Finance',
            'STOCK_5': 'Healthcare'
        }
        
        sector_recommendations = self.recommender.calculate_sector_recommendations(
            {k: self.test_data[k] for k in sectors.keys()},
            sectors
        )
        
        # Check sector recommendations
        self.assertIsInstance(sector_recommendations, dict)
        self.assertEqual(
            set(sector_recommendations.keys()),
            set(sectors.values())
        )

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with empty data
        with self.assertRaises(Exception):
            self.recommender.generate_recommendations({})
        
        # Test with invalid data format
        invalid_data = {'STOCK_1': pd.DataFrame({'close': [10, 20]})}
        with self.assertRaises(Exception):
            self.recommender.analyze_stock(invalid_data['STOCK_1'], 'STOCK_1')

    def test_recommendation_consistency(self):
        """Test consistency of recommendations."""
        # Generate recommendations multiple times
        recommendations1 = self.recommender.generate_recommendations(self.test_data)
        recommendations2 = self.recommender.generate_recommendations(self.test_data)
        
        # Check if recommendations are consistent
        for r1, r2 in zip(recommendations1, recommendations2):
            self.assertEqual(r1['symbol'], r2['symbol'])
            self.assertEqual(r1['score'], r2['score'])

    def test_recommendation_thresholds(self):
        """Test recommendation thresholds and categories."""
        stock_data = self.test_data['STOCK_1'].copy()
        
        # Test strong buy conditions
        stock_data['RSI'] = 30
        stock_data['MACD'] = 2
        strong_buy = self.recommender.analyze_stock(stock_data, 'STOCK_1')
        self.assertIn('buy', strong_buy['recommendation'].lower())
        
        # Test strong sell conditions
        stock_data['RSI'] = 80
        stock_data['MACD'] = -2
        strong_sell = self.recommender.analyze_stock(stock_data, 'STOCK_1')
        self.assertIn('sell', strong_sell['recommendation'].lower())

if __name__ == '__main__':
    unittest.main()
