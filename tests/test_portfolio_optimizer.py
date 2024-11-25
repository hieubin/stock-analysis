import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.portfolio_optimizer import PortfolioOptimizer

class TestPortfolioOptimizer(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.optimizer = PortfolioOptimizer()
        
        # Create sample stock data for multiple stocks
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        num_stocks = 5
        
        # Generate random returns for multiple stocks
        returns_data = {}
        for i in range(num_stocks):
            stock_returns = np.random.normal(0.001, 0.02, len(dates))
            returns_data[f'STOCK_{i+1}'] = stock_returns
        
        self.returns_df = pd.DataFrame(returns_data, index=dates)
        self.risk_free_rate = 0.02  # 2% annual rate

    def test_calculate_portfolio_metrics(self):
        """Test portfolio metrics calculation."""
        # Create equal weights
        weights = np.array([0.2] * 5)
        
        metrics = self.optimizer.calculate_portfolio_metrics(
            self.returns_df,
            weights,
            self.risk_free_rate
        )
        
        # Check if all metrics are present
        required_metrics = [
            'return', 'volatility', 'sharpe_ratio'
        ]
        for metric in required_metrics:
            self.assertIn(metric, metrics)
        
        # Check metric properties
        self.assertIsInstance(metrics['return'], float)
        self.assertGreater(metrics['volatility'], 0)
        self.assertIsInstance(metrics['sharpe_ratio'], float)

    def test_optimize_portfolio(self):
        """Test portfolio optimization."""
        optimized = self.optimizer.optimize_portfolio(
            self.returns_df,
            self.risk_free_rate
        )
        
        # Check optimization results
        self.assertIn('weights', optimized)
        self.assertIn('metrics', optimized)
        
        # Check weights properties
        weights = optimized['weights']
        self.assertEqual(len(weights), len(self.returns_df.columns))
        self.assertAlmostEqual(sum(weights), 1.0, places=6)
        self.assertTrue(all(w >= 0 for w in weights))

    def test_generate_efficient_frontier(self):
        """Test efficient frontier generation."""
        frontier = self.optimizer.generate_efficient_frontier(
            self.returns_df,
            self.risk_free_rate,
            num_portfolios=50
        )
        
        # Check frontier properties
        self.assertGreater(len(frontier), 0)
        self.assertTrue(all(isinstance(p, dict) for p in frontier))
        
        # Check if frontier is properly ordered
        returns = [p['metrics']['return'] for p in frontier]
        self.assertEqual(returns, sorted(returns))

    def test_get_optimal_portfolio(self):
        """Test optimal portfolio selection."""
        target_return = 0.10  # 10% annual return
        optimal = self.optimizer.get_optimal_portfolio(
            self.returns_df,
            self.risk_free_rate,
            target_return
        )
        
        # Check optimal portfolio properties
        self.assertIn('weights', optimal)
        self.assertIn('metrics', optimal)
        
        # Check if target return is approximately achieved
        self.assertAlmostEqual(
            optimal['metrics']['return'],
            target_return,
            places=2
        )

    def test_calculate_portfolio_var(self):
        """Test portfolio VaR calculation."""
        weights = np.array([0.2] * 5)
        confidence_level = 0.95
        
        var = self.optimizer.calculate_portfolio_var(
            self.returns_df,
            weights,
            confidence_level
        )
        
        # Check VaR properties
        self.assertLess(var, 0)
        self.assertIsInstance(var, float)

    def test_rebalance_portfolio(self):
        """Test portfolio rebalancing."""
        initial_weights = np.array([0.2] * 5)
        current_prices = pd.Series([100, 110, 95, 105, 98], 
                                 index=self.returns_df.columns)
        
        rebalanced = self.optimizer.rebalance_portfolio(
            initial_weights,
            current_prices
        )
        
        # Check rebalancing results
        self.assertEqual(len(rebalanced), len(initial_weights))
        self.assertAlmostEqual(sum(rebalanced), 1.0, places=6)

    def test_calculate_tracking_error(self):
        """Test tracking error calculation."""
        weights = np.array([0.2] * 5)
        benchmark_returns = pd.Series(
            np.random.normal(0.001, 0.02, len(self.returns_df)),
            index=self.returns_df.index
        )
        
        tracking_error = self.optimizer.calculate_tracking_error(
            self.returns_df,
            weights,
            benchmark_returns
        )
        
        # Check tracking error properties
        self.assertGreater(tracking_error, 0)
        self.assertIsInstance(tracking_error, float)

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test with very few assets
        single_stock = self.returns_df.iloc[:, 0:1]
        with self.assertRaises(Exception):
            self.optimizer.optimize_portfolio(
                single_stock,
                self.risk_free_rate
            )
        
        # Test with invalid weights
        invalid_weights = np.array([0.5] * 5)  # Sum > 1
        with self.assertRaises(Exception):
            self.optimizer.calculate_portfolio_metrics(
                self.returns_df,
                invalid_weights,
                self.risk_free_rate
            )

    def test_optimization_constraints(self):
        """Test portfolio optimization with constraints."""
        # Test minimum weight constraint
        min_weight = 0.1
        optimized = self.optimizer.optimize_portfolio(
            self.returns_df,
            self.risk_free_rate,
            min_weight=min_weight
        )
        
        self.assertTrue(all(w >= min_weight for w in optimized['weights']))
        
        # Test maximum weight constraint
        max_weight = 0.3
        optimized = self.optimizer.optimize_portfolio(
            self.returns_df,
            self.risk_free_rate,
            max_weight=max_weight
        )
        
        self.assertTrue(all(w <= max_weight for w in optimized['weights']))

    def test_portfolio_performance(self):
        """Test portfolio performance calculation."""
        # Test with different weight allocations
        weight_sets = [
            np.array([0.2] * 5),  # Equal weights
            np.array([0.4, 0.3, 0.2, 0.1, 0.0]),  # Concentrated
            np.array([0.33, 0.33, 0.34, 0.0, 0.0])  # Three assets
        ]
        
        for weights in weight_sets:
            metrics = self.optimizer.calculate_portfolio_metrics(
                self.returns_df,
                weights,
                self.risk_free_rate
            )
            
            # Check basic properties
            self.assertGreater(metrics['volatility'], 0)
            self.assertTrue(
                abs(metrics['return']) < 1.0  # Reasonable return range
            )

if __name__ == '__main__':
    unittest.main()
