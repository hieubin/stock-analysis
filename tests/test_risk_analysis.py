import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.risk_analysis import RiskAnalyzer

class TestRiskAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.analyzer = RiskAnalyzer()
        
        # Create sample price data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.test_data = pd.DataFrame({
            'date': dates,
            'close': np.random.uniform(10, 20, len(dates)),
            'volume': np.random.randint(1000, 10000, len(dates))
        })
        
        # Calculate daily returns
        self.test_data['returns'] = self.test_data['close'].pct_change()
        
        # Create market data
        self.market_data = pd.DataFrame({
            'date': dates,
            'close': np.random.uniform(100, 200, len(dates))
        })
        self.market_data['returns'] = self.market_data['close'].pct_change()

    def test_calculate_volatility(self):
        """Test volatility calculation."""
        volatility = self.analyzer.calculate_volatility(self.test_data['returns'])
        
        # Check volatility properties
        self.assertGreater(volatility, 0)
        self.assertIsInstance(volatility, float)
        
        # Test with constant returns
        constant_returns = pd.Series([0.01] * 100)
        constant_volatility = self.analyzer.calculate_volatility(constant_returns)
        self.assertAlmostEqual(constant_volatility, 0)

    def test_calculate_beta(self):
        """Test beta calculation."""
        beta = self.analyzer.calculate_beta(
            self.test_data['returns'],
            self.market_data['returns']
        )
        
        # Check beta properties
        self.assertIsInstance(beta, float)
        
        # Test with perfectly correlated returns
        self.test_data['returns'] = self.market_data['returns']
        perfect_beta = self.analyzer.calculate_beta(
            self.test_data['returns'],
            self.market_data['returns']
        )
        self.assertAlmostEqual(perfect_beta, 1.0, places=2)

    def test_calculate_sharpe_ratio(self):
        """Test Sharpe ratio calculation."""
        risk_free_rate = 0.02  # 2% annual rate
        sharpe = self.analyzer.calculate_sharpe_ratio(
            self.test_data['returns'],
            risk_free_rate
        )
        
        # Check Sharpe ratio properties
        self.assertIsInstance(sharpe, float)
        
        # Test with high returns and low volatility
        high_returns = pd.Series([0.01] * 100)  # 1% daily return
        high_sharpe = self.analyzer.calculate_sharpe_ratio(high_returns, risk_free_rate)
        self.assertGreater(high_sharpe, 0)

    def test_calculate_sortino_ratio(self):
        """Test Sortino ratio calculation."""
        risk_free_rate = 0.02
        sortino = self.analyzer.calculate_sortino_ratio(
            self.test_data['returns'],
            risk_free_rate
        )
        
        # Check Sortino ratio properties
        self.assertIsInstance(sortino, float)
        
        # Test with only positive returns
        positive_returns = pd.Series([0.01] * 100)
        positive_sortino = self.analyzer.calculate_sortino_ratio(
            positive_returns,
            risk_free_rate
        )
        self.assertGreater(positive_sortino, 0)

    def test_calculate_maximum_drawdown(self):
        """Test maximum drawdown calculation."""
        max_dd = self.analyzer.calculate_maximum_drawdown(self.test_data['close'])
        
        # Check maximum drawdown properties
        self.assertLessEqual(max_dd, 0)
        self.assertGreaterEqual(max_dd, -1)
        
        # Test with constantly increasing prices
        increasing_prices = pd.Series(range(1, 101))
        increasing_dd = self.analyzer.calculate_maximum_drawdown(increasing_prices)
        self.assertEqual(increasing_dd, 0)

    def test_calculate_var(self):
        """Test Value at Risk calculation."""
        confidence_level = 0.95
        var = self.analyzer.calculate_var(
            self.test_data['returns'],
            confidence_level
        )
        
        # Check VaR properties
        self.assertLess(var, 0)  # VaR should be negative
        self.assertIsInstance(var, float)
        
        # Test with normal distribution
        normal_returns = np.random.normal(0.001, 0.02, 1000)
        normal_var = self.analyzer.calculate_var(
            pd.Series(normal_returns),
            confidence_level
        )
        self.assertLess(normal_var, 0)

    def test_calculate_risk_metrics(self):
        """Test comprehensive risk metrics calculation."""
        risk_metrics = self.analyzer.calculate_risk_metrics(
            self.test_data['returns'],
            self.market_data['returns']
        )
        
        # Check if all metrics are present
        required_metrics = [
            'volatility', 'beta', 'sharpe_ratio',
            'sortino_ratio', 'max_drawdown', 'var_95'
        ]
        for metric in required_metrics:
            self.assertIn(metric, risk_metrics)
        
        # Check metric types and bounds
        self.assertGreater(risk_metrics['volatility'], 0)
        self.assertGreaterEqual(risk_metrics['max_drawdown'], -1)
        self.assertLess(risk_metrics['var_95'], 0)

    def test_get_risk_rating(self):
        """Test risk rating calculation."""
        risk_metrics = self.analyzer.calculate_risk_metrics(
            self.test_data['returns'],
            self.market_data['returns']
        )
        risk_rating = self.analyzer.get_risk_rating(risk_metrics)
        
        # Check risk rating properties
        self.assertIsInstance(risk_rating, str)
        self.assertIn(risk_rating, ['Low', 'Medium', 'High'])

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with very short data
        short_data = pd.Series(np.random.random(5))
        with self.assertRaises(Exception):
            self.analyzer.calculate_risk_metrics(
                short_data,
                self.market_data['returns']
            )
        
        # Test with NaN values
        nan_data = self.test_data['returns'].copy()
        nan_data[10:20] = np.nan
        with self.assertRaises(Exception):
            self.analyzer.calculate_volatility(nan_data)

    def test_risk_consistency(self):
        """Test consistency of risk measurements."""
        # Calculate risk metrics for original and scaled returns
        original_metrics = self.analyzer.calculate_risk_metrics(
            self.test_data['returns'],
            self.market_data['returns']
        )
        
        scaled_returns = self.test_data['returns'] * 2
        scaled_metrics = self.analyzer.calculate_risk_metrics(
            scaled_returns,
            self.market_data['returns']
        )
        
        # Check that volatility scales appropriately
        self.assertAlmostEqual(
            scaled_metrics['volatility'],
            original_metrics['volatility'] * 2,
            places=2
        )
        
        # Check that beta scales appropriately
        self.assertAlmostEqual(
            scaled_metrics['beta'],
            original_metrics['beta'] * 2,
            places=2
        )

if __name__ == '__main__':
    unittest.main()
