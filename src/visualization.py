import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Optional
import logging
from pathlib import Path
import stats

logger = logging.getLogger(__name__)

class StockVisualizer:
    def __init__(self, output_dir: str = 'data/visualizations'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('default')  # Use default style instead of seaborn
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        self.figsize = (12, 8)

    def plot_price_history(self, df: pd.DataFrame, symbol: str, 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None) -> str:
        """Plot stock price history with volume."""
        try:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), height_ratios=[3, 1])
            
            # Filter date range if specified
            if start_date:
                df = df[df['date'] >= start_date]
            if end_date:
                df = df[df['date'] <= end_date]
            
            # Price plot
            ax1.plot(df['date'], df['close'], label='Close Price')
            ax1.plot(df['date'], df['SMA_short'], label=f'SMA ({df["SMA_short"].name})')
            ax1.plot(df['date'], df['SMA_medium'], label=f'SMA ({df["SMA_medium"].name})')
            
            ax1.set_title(f'{symbol} Stock Price History')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Price')
            ax1.legend()
            ax1.grid(True)
            
            # Volume plot
            ax2.bar(df['date'], df['volume'], alpha=0.5)
            ax2.set_ylabel('Volume')
            ax2.grid(True)
            
            plt.tight_layout()
            
            # Save plot
            output_path = self.output_dir / f'{symbol}_price_history.png'
            plt.savefig(output_path)
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error plotting price history for {symbol}: {e}")
            raise

    def plot_technical_indicators(self, df: pd.DataFrame, symbol: str) -> str:
        """Plot technical indicators (RSI, MACD, Bollinger Bands)."""
        try:
            fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 12))
            
            # Price and Bollinger Bands
            ax1.plot(df['date'], df['close'], label='Close Price')
            ax1.plot(df['date'], df['BB_Upper'], 'r--', label='Upper BB')
            ax1.plot(df['date'], df['BB_Middle'], 'g--', label='Middle BB')
            ax1.plot(df['date'], df['BB_Lower'], 'r--', label='Lower BB')
            ax1.set_title(f'{symbol} Price and Bollinger Bands')
            ax1.legend()
            ax1.grid(True)
            
            # RSI
            ax2.plot(df['date'], df['RSI'], label='RSI')
            ax2.axhline(y=70, color='r', linestyle='--')
            ax2.axhline(y=30, color='g', linestyle='--')
            ax2.set_title('RSI')
            ax2.set_ylim(0, 100)
            ax2.grid(True)
            
            # MACD
            ax3.plot(df['date'], df['MACD'], label='MACD')
            ax3.plot(df['date'], df['Signal_Line'], label='Signal Line')
            ax3.bar(df['date'], df['MACD'] - df['Signal_Line'], alpha=0.3)
            ax3.set_title('MACD')
            ax3.legend()
            ax3.grid(True)
            
            plt.tight_layout()
            
            # Save plot
            output_path = self.output_dir / f'{symbol}_technical_indicators.png'
            plt.savefig(output_path)
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error plotting technical indicators for {symbol}: {e}")
            raise

    def plot_correlation_matrix(self, df: pd.DataFrame, symbols: List[str]) -> str:
        """Plot correlation matrix of multiple stocks."""
        try:
            # Calculate correlation matrix
            returns = pd.DataFrame()
            for symbol in symbols:
                returns[symbol] = df[df['symbol'] == symbol]['close'].pct_change()
            
            corr_matrix = returns.corr()
            
            # Plot
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Stock Returns Correlation Matrix')
            
            # Save plot
            output_path = self.output_dir / 'correlation_matrix.png'
            plt.savefig(output_path)
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error plotting correlation matrix: {e}")
            raise

    def plot_risk_metrics(self, risk_metrics: Dict[str, float], symbol: str) -> str:
        """Plot risk metrics in a radar chart."""
        try:
            metrics = ['volatility', 'sharpe_ratio', 'sortino_ratio', 
                      'max_drawdown', 'var_95', 'beta']
            values = [risk_metrics.get(m, 0) for m in metrics]
            
            # Normalize values
            values_norm = [(v - min(values)) / (max(values) - min(values)) for v in values]
            
            # Radar chart
            angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
            values_norm = np.concatenate((values_norm, [values_norm[0]]))  # complete the loop
            angles = np.concatenate((angles, [angles[0]]))  # complete the loop
            
            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
            ax.plot(angles, values_norm)
            ax.fill(angles, values_norm, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(metrics)
            ax.set_title(f'{symbol} Risk Metrics')
            
            # Save plot
            output_path = self.output_dir / f'{symbol}_risk_metrics.png'
            plt.savefig(output_path)
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error plotting risk metrics for {symbol}: {e}")
            raise

    def plot_portfolio_composition(self, weights: Dict[str, float]) -> str:
        """Plot portfolio composition as a pie chart."""
        try:
            plt.figure(figsize=(10, 8))
            plt.pie(weights.values(), labels=weights.keys(), autopct='%1.1f%%')
            plt.title('Portfolio Composition')
            
            # Save plot
            output_path = self.output_dir / 'portfolio_composition.png'
            plt.savefig(output_path)
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error plotting portfolio composition: {e}")
            raise

    def plot_returns_distribution(self, df: pd.DataFrame, symbol: str) -> str:
        """Plot returns distribution with normal distribution fit."""
        try:
            returns = df['close'].pct_change().dropna()
            
            plt.figure(figsize=(10, 6))
            sns.histplot(returns, kde=True, stat='density')
            
            # Fit normal distribution
            mu, std = returns.mean(), returns.std()
            x = np.linspace(returns.min(), returns.max(), 100)
            p = stats.norm.pdf(x, mu, std)
            plt.plot(x, p, 'r-', lw=2, label='Normal Distribution')
            
            plt.title(f'{symbol} Returns Distribution')
            plt.xlabel('Returns')
            plt.ylabel('Density')
            plt.legend()
            
            # Save plot
            output_path = self.output_dir / f'{symbol}_returns_distribution.png'
            plt.savefig(output_path)
            plt.close()
            
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Error plotting returns distribution for {symbol}: {e}")
            raise
