import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from scipy.optimize import minimize
from datetime import datetime, timedelta

from .risk_analysis import RiskAnalyzer
from .constants import TIME_PERIODS

logger = logging.getLogger(__name__)

class PortfolioOptimizer:
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_analyzer = RiskAnalyzer(risk_free_rate)
        self.risk_free_rate = risk_free_rate

    def calculate_portfolio_metrics(self, returns: pd.DataFrame, weights: np.ndarray) -> Tuple[float, float, float]:
        """Calculate portfolio return, volatility, and Sharpe ratio."""
        portfolio_return = np.sum(returns.mean() * weights) * 252
        portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
        return portfolio_return, portfolio_volatility, sharpe_ratio

    def negative_sharpe_ratio(self, weights: np.ndarray, returns: pd.DataFrame) -> float:
        """Calculate negative Sharpe ratio for optimization."""
        portfolio_return, portfolio_volatility, sharpe_ratio = self.calculate_portfolio_metrics(returns, weights)
        return -sharpe_ratio

    def optimize_portfolio(self, stock_data: Dict[str, pd.DataFrame], 
                         constraints: Dict[str, float] = None) -> Dict[str, any]:
        """Optimize portfolio weights using Modern Portfolio Theory."""
        try:
            # Prepare returns data
            returns_data = pd.DataFrame()
            for symbol, df in stock_data.items():
                returns_data[symbol] = df['close'].pct_change().dropna()
            
            num_assets = len(stock_data)
            
            # Initial weights
            weights = np.array([1/num_assets] * num_assets)
            
            # Constraints
            bounds = [(0, 1) for _ in range(num_assets)]  # Each weight between 0 and 1
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Weights sum to 1
            ]
            
            if constraints:
                # Add minimum and maximum weight constraints if specified
                min_weight = constraints.get('min_weight', 0)
                max_weight = constraints.get('max_weight', 1)
                bounds = [(min_weight, max_weight) for _ in range(num_assets)]
            
            # Optimize portfolio
            result = minimize(
                self.negative_sharpe_ratio,
                weights,
                args=(returns_data,),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
            
            if not result.success:
                logger.warning(f"Portfolio optimization failed: {result.message}")
            
            # Calculate optimal portfolio metrics
            optimal_weights = result.x
            portfolio_return, portfolio_volatility, sharpe_ratio = self.calculate_portfolio_metrics(
                returns_data, optimal_weights
            )
            
            # Calculate additional metrics
            portfolio_beta = self.calculate_portfolio_beta(returns_data, optimal_weights)
            portfolio_var = self.calculate_portfolio_var(returns_data, optimal_weights)
            
            return {
                'weights': dict(zip(stock_data.keys(), optimal_weights)),
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'beta': portfolio_beta,
                'var_95': portfolio_var
            }
            
        except Exception as e:
            logger.error(f"Error optimizing portfolio: {e}")
            raise

    def calculate_portfolio_beta(self, returns: pd.DataFrame, weights: np.ndarray) -> float:
        """Calculate portfolio beta relative to market."""
        try:
            # Assuming first asset is market index
            market_returns = returns.iloc[:, 0]
            portfolio_returns = np.dot(returns, weights)
            
            covariance = np.cov(portfolio_returns, market_returns)[0, 1]
            market_variance = np.var(market_returns)
            
            return covariance / market_variance
            
        except Exception as e:
            logger.error(f"Error calculating portfolio beta: {e}")
            return 0.0

    def calculate_portfolio_var(self, returns: pd.DataFrame, weights: np.ndarray,
                              confidence_level: float = 0.95) -> float:
        """Calculate portfolio Value at Risk."""
        try:
            portfolio_returns = np.dot(returns, weights)
            return np.percentile(portfolio_returns, (1 - confidence_level) * 100)
            
        except Exception as e:
            logger.error(f"Error calculating portfolio VaR: {e}")
            return 0.0

    def generate_efficient_frontier(self, stock_data: Dict[str, pd.DataFrame], 
                                 num_portfolios: int = 1000) -> pd.DataFrame:
        """Generate efficient frontier points."""
        try:
            returns_data = pd.DataFrame()
            for symbol, df in stock_data.items():
                returns_data[symbol] = df['close'].pct_change().dropna()
            
            num_assets = len(stock_data)
            results = []
            
            for _ in range(num_portfolios):
                weights = np.random.random(num_assets)
                weights = weights / np.sum(weights)
                
                portfolio_return, portfolio_volatility, sharpe_ratio = self.calculate_portfolio_metrics(
                    returns_data, weights
                )
                
                results.append({
                    'return': portfolio_return,
                    'volatility': portfolio_volatility,
                    'sharpe_ratio': sharpe_ratio,
                    'weights': weights
                })
            
            return pd.DataFrame(results)
            
        except Exception as e:
            logger.error(f"Error generating efficient frontier: {e}")
            raise

    def rebalance_portfolio(self, current_weights: Dict[str, float], 
                          optimal_weights: Dict[str, float],
                          threshold: float = 0.05) -> Dict[str, float]:
        """Calculate required portfolio rebalancing trades."""
        try:
            rebalancing_trades = {}
            
            for symbol in optimal_weights:
                current = current_weights.get(symbol, 0)
                target = optimal_weights[symbol]
                diff = target - current
                
                if abs(diff) > threshold:
                    rebalancing_trades[symbol] = diff
            
            return rebalancing_trades
            
        except Exception as e:
            logger.error(f"Error calculating rebalancing trades: {e}")
            return {}

    def calculate_portfolio_performance(self, weights: Dict[str, float],
                                     stock_data: Dict[str, pd.DataFrame],
                                     start_date: str,
                                     end_date: str) -> Dict[str, float]:
        """Calculate historical portfolio performance metrics."""
        try:
            # Prepare portfolio returns
            portfolio_returns = pd.Series(0, index=pd.date_range(start_date, end_date))
            
            for symbol, weight in weights.items():
                if symbol in stock_data:
                    df = stock_data[symbol]
                    returns = df['close'].pct_change()
                    portfolio_returns += returns * weight
            
            # Calculate metrics
            total_return = (1 + portfolio_returns).prod() - 1
            volatility = portfolio_returns.std() * np.sqrt(252)
            sharpe = (portfolio_returns.mean() * 252 - self.risk_free_rate) / volatility
            max_drawdown = (portfolio_returns.cumsum().expanding().max() - portfolio_returns.cumsum()).max()
            
            return {
                'total_return': total_return,
                'annualized_return': (1 + total_return) ** (252 / len(portfolio_returns)) - 1,
                'volatility': volatility,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_drawdown,
                'var_95': np.percentile(portfolio_returns, 5),
                'best_month': portfolio_returns.resample('M').sum().max(),
                'worst_month': portfolio_returns.resample('M').sum().min()
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio performance: {e}")
            raise
