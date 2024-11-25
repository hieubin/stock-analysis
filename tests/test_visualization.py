import unittest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import matplotlib.pyplot as plt

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.visualization import StockVisualizer

class TestStockVisualizer(unittest.TestCase):
    def setUp(self):
        """Set up test data."""
        self.visualizer = StockVisualizer()
        
        # Create sample stock data
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        self.test_data = pd.DataFrame({
            'date': dates,
            'open': np.random.uniform(10, 20, len(dates)),
            'high': np.random.uniform(15, 25, len(dates)),
            'low': np.random.uniform(5, 15, len(dates)),
            'close': np.random.uniform(10, 20, len(dates)),
            'volume': np.random.randint(1000, 10000, len(dates)),
            'RSI': np.random.uniform(30, 70, len(dates)),
            'MACD': np.random.uniform(-1, 1, len(dates)),
            'Signal_Line': np.random.uniform(-1, 1, len(dates)),
            'SMA_short': np.random.uniform(10, 20, len(dates)),
            'SMA_medium': np.random.uniform(10, 20, len(dates))
        })
        self.test_data.set_index('date', inplace=True)
        
        # Create portfolio data
        self.portfolio_data = {}
        for i in range(5):
            self.portfolio_data[f'STOCK_{i+1}'] = pd.DataFrame({
                'date': dates,
                'close': np.random.uniform(10, 20, len(dates)),
                'returns': np.random.normal(0.001, 0.02, len(dates))
            }).set_index('date')

    def test_plot_price_history(self):
        """Test price history plot generation."""
        fig = self.visualizer.plot_price_history(
            self.test_data,
            'Test Stock'
        )
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 2)  # Price and volume subplots
        
        plt.close(fig)

    def test_plot_technical_indicators(self):
        """Test technical indicators plot generation."""
        fig = self.visualizer.plot_technical_indicators(
            self.test_data,
            'Test Stock'
        )
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertGreater(len(fig.axes), 2)  # Multiple indicator subplots
        
        plt.close(fig)

    def test_plot_correlation_matrix(self):
        """Test correlation matrix plot generation."""
        returns_data = pd.DataFrame({
            stock: data['returns']
            for stock, data in self.portfolio_data.items()
        })
        
        fig = self.visualizer.plot_correlation_matrix(returns_data)
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 1)
        
        plt.close(fig)

    def test_plot_efficient_frontier(self):
        """Test efficient frontier plot generation."""
        # Generate sample portfolio data
        num_portfolios = 1000
        returns = np.random.normal(0.1, 0.2, num_portfolios)
        volatilities = np.random.uniform(0.1, 0.3, num_portfolios)
        sharpe_ratios = returns / volatilities
        
        fig = self.visualizer.plot_efficient_frontier(
            returns,
            volatilities,
            sharpe_ratios
        )
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 1)
        
        plt.close(fig)

    def test_plot_portfolio_composition(self):
        """Test portfolio composition plot generation."""
        weights = {
            'STOCK_1': 0.2,
            'STOCK_2': 0.3,
            'STOCK_3': 0.15,
            'STOCK_4': 0.25,
            'STOCK_5': 0.1
        }
        
        fig = self.visualizer.plot_portfolio_composition(weights)
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 1)
        
        plt.close(fig)

    def test_plot_returns_distribution(self):
        """Test returns distribution plot generation."""
        returns = self.test_data['close'].pct_change().dropna()
        
        fig = self.visualizer.plot_returns_distribution(
            returns,
            'Test Stock'
        )
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 1)
        
        plt.close(fig)

    def test_plot_risk_metrics(self):
        """Test risk metrics plot generation."""
        risk_metrics = {
            'volatility': 0.2,
            'beta': 1.1,
            'sharpe_ratio': 1.5,
            'sortino_ratio': 2.0,
            'max_drawdown': -0.15,
            'var_95': -0.02
        }
        
        fig = self.visualizer.plot_risk_metrics(risk_metrics)
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 1)
        
        plt.close(fig)

    def test_plot_portfolio_performance(self):
        """Test portfolio performance plot generation."""
        portfolio_values = pd.Series(
            np.random.uniform(900000, 1100000, len(self.test_data.index)),
            index=self.test_data.index
        )
        
        fig = self.visualizer.plot_portfolio_performance(portfolio_values)
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 1)
        
        plt.close(fig)

    def test_plot_sector_allocation(self):
        """Test sector allocation plot generation."""
        sector_weights = {
            'Technology': 0.3,
            'Finance': 0.25,
            'Healthcare': 0.2,
            'Consumer': 0.15,
            'Energy': 0.1
        }
        
        fig = self.visualizer.plot_sector_allocation(sector_weights)
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 1)
        
        plt.close(fig)

    def test_plot_recommendation_summary(self):
        """Test recommendation summary plot generation."""
        recommendations = [
            {'symbol': 'STOCK_1', 'score': 0.8},
            {'symbol': 'STOCK_2', 'score': 0.7},
            {'symbol': 'STOCK_3', 'score': 0.6},
            {'symbol': 'STOCK_4', 'score': 0.5},
            {'symbol': 'STOCK_5', 'score': 0.4}
        ]
        
        fig = self.visualizer.plot_recommendation_summary(recommendations)
        
        # Check plot properties
        self.assertIsInstance(fig, plt.Figure)
        self.assertEqual(len(fig.axes), 1)
        
        plt.close(fig)

    def test_save_plot(self):
        """Test plot saving functionality."""
        # Create a simple plot
        fig = self.visualizer.plot_returns_distribution(
            self.test_data['close'].pct_change().dropna(),
            'Test Stock'
        )
        
        # Save plot to temporary file
        temp_file = 'test_plot.png'
        self.visualizer.save_plot(fig, temp_file)
        
        # Check if file exists and then remove it
        self.assertTrue(Path(temp_file).exists())
        Path(temp_file).unlink()
        
        plt.close(fig)

    def test_plot_customization(self):
        """Test plot customization options."""
        fig = self.visualizer.plot_price_history(
            self.test_data,
            'Test Stock',
            title='Custom Title',
            color_scheme='seaborn',
            show_volume=True,
            show_grid=True
        )
        
        # Check customization
        self.assertEqual(fig.axes[0].get_title(), 'Custom Title')
        self.assertTrue(fig.axes[0].get_grid())
        
        plt.close(fig)

if __name__ == '__main__':
    unittest.main()
