import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging
from scipy import stats

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate

    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate daily returns."""
        return prices.pct_change().dropna()

    def calculate_volatility(self, returns: pd.Series, annualize: bool = True) -> float:
        """Calculate volatility (standard deviation of returns)."""
        vol = returns.std()
        if annualize:
            vol *= np.sqrt(252)  # Annualize daily volatility
        return vol

    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe Ratio."""
        excess_returns = returns - self.risk_free_rate/252  # Daily risk-free rate
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std()

    def calculate_sortino_ratio(self, returns: pd.Series) -> float:
        """Calculate Sortino Ratio."""
        excess_returns = returns - self.risk_free_rate/252
        downside_returns = excess_returns[excess_returns < 0]
        if len(downside_returns) == 0:
            return 0
        downside_std = np.sqrt(np.mean(downside_returns**2))
        if downside_std == 0:
            return 0
        return np.sqrt(252) * excess_returns.mean() / downside_std

    def calculate_max_drawdown(self, prices: pd.Series) -> tuple:
        """Calculate Maximum Drawdown and its duration."""
        roll_max = prices.expanding().max()
        drawdowns = prices/roll_max - 1
        max_drawdown = drawdowns.min()
        
        # Find drawdown duration
        end_idx = drawdowns.idxmin()
        peak_idx = prices[:end_idx].idxmax()
        duration = (end_idx - peak_idx).days
        
        return max_drawdown, duration

    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk."""
        return np.percentile(returns, (1 - confidence_level) * 100)

    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (Expected Shortfall)."""
        var = self.calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()

    def calculate_beta(self, returns: pd.Series, market_returns: pd.Series) -> float:
        """Calculate Beta relative to market."""
        covariance = returns.cov(market_returns)
        market_variance = market_returns.var()
        if market_variance == 0:
            return 0
        return covariance / market_variance

    def calculate_alpha(self, returns: pd.Series, market_returns: pd.Series) -> float:
        """Calculate Alpha (Jensen's Alpha)."""
        beta = self.calculate_beta(returns, market_returns)
        return returns.mean() - (self.risk_free_rate/252 + beta * (market_returns.mean() - self.risk_free_rate/252))

    def calculate_information_ratio(self, returns: pd.Series, benchmark_returns: pd.Series) -> float:
        """Calculate Information Ratio."""
        active_returns = returns - benchmark_returns
        if active_returns.std() == 0:
            return 0
        return np.sqrt(252) * active_returns.mean() / active_returns.std()

    def calculate_risk_metrics(self, prices: pd.Series, market_prices: Optional[pd.Series] = None) -> Dict[str, float]:
        """Calculate comprehensive risk metrics for a stock."""
        try:
            returns = self.calculate_returns(prices)
            market_returns = None if market_prices is None else self.calculate_returns(market_prices)
            
            metrics = {
                'volatility': self.calculate_volatility(returns),
                'sharpe_ratio': self.calculate_sharpe_ratio(returns),
                'sortino_ratio': self.calculate_sortino_ratio(returns),
                'var_95': self.calculate_var(returns),
                'cvar_95': self.calculate_cvar(returns),
            }
            
            # Maximum drawdown
            max_dd, dd_duration = self.calculate_max_drawdown(prices)
            metrics['max_drawdown'] = max_dd
            metrics['drawdown_duration'] = dd_duration
            
            # Market-relative metrics if market data is provided
            if market_returns is not None:
                metrics.update({
                    'beta': self.calculate_beta(returns, market_returns),
                    'alpha': self.calculate_alpha(returns, market_returns),
                    'information_ratio': self.calculate_information_ratio(returns, market_returns)
                })
            
            # Additional statistical metrics
            metrics.update({
                'skewness': returns.skew(),
                'kurtosis': returns.kurtosis(),
                'daily_var_95': self.calculate_var(returns),
                'weekly_var_95': self.calculate_var(returns.rolling(5).sum()),
                'monthly_var_95': self.calculate_var(returns.rolling(21).sum())
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating risk metrics: {e}")
            raise

    def get_risk_rating(self, metrics: Dict[str, float]) -> str:
        """Determine risk rating based on calculated metrics."""
        try:
            # Define thresholds for risk categories
            volatility_thresholds = {
                'Low': 0.15,
                'Medium': 0.25,
                'High': 0.35
            }
            
            sharpe_thresholds = {
                'Poor': 0.5,
                'Fair': 1.0,
                'Good': 1.5
            }
            
            # Calculate risk score
            vol_score = 1 if metrics['volatility'] < volatility_thresholds['Low'] else \
                       2 if metrics['volatility'] < volatility_thresholds['Medium'] else \
                       3 if metrics['volatility'] < volatility_thresholds['High'] else 4
                       
            sharpe_score = 3 if metrics['sharpe_ratio'] > sharpe_thresholds['Good'] else \
                          2 if metrics['sharpe_ratio'] > sharpe_thresholds['Fair'] else \
                          1 if metrics['sharpe_ratio'] > sharpe_thresholds['Poor'] else 0
            
            drawdown_score = 1 if abs(metrics['max_drawdown']) < 0.1 else \
                            2 if abs(metrics['max_drawdown']) < 0.2 else \
                            3 if abs(metrics['max_drawdown']) < 0.3 else 4
            
            # Combined risk score
            total_score = vol_score + (4 - sharpe_score) + drawdown_score
            
            # Map total score to risk rating
            if total_score <= 5:
                return 'Low Risk'
            elif total_score <= 8:
                return 'Medium Risk'
            elif total_score <= 11:
                return 'High Risk'
            else:
                return 'Very High Risk'
                
        except Exception as e:
            logger.error(f"Error determining risk rating: {e}")
            return 'Unknown Risk'
