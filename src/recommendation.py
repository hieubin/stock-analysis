import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta
from pathlib import Path

from .data_processing import StockDataProcessor
from .constants import WEIGHTS, PROCESSED_DATA_DIR

logger = logging.getLogger(__name__)

class StockRecommender:
    def __init__(self):
        self.data_processor = StockDataProcessor()
        self.recommendations: Dict[str, float] = {}

    def analyze_stock(self, symbol: str) -> Dict[str, float]:
        """Analyze a single stock and return its metrics."""
        try:
            # Process stock data
            df = self.data_processor.process_data(symbol)
            
            # Get latest indicators
            indicators = self.data_processor.get_market_indicators(df)
            
            # Calculate recommendation score
            score = self.data_processor.get_recommendation_score(symbol)
            
            return {
                'symbol': symbol,
                'score': score,
                'metrics': indicators
            }
        except Exception as e:
            logger.error(f"Error analyzing stock {symbol}: {e}")
            return {'symbol': symbol, 'score': 0.0, 'metrics': {}}

    def get_top_recommendations(self, symbols: List[str], top_n: int = 10) -> List[Dict]:
        """Generate top N stock recommendations."""
        try:
            all_recommendations = []
            
            for symbol in symbols:
                analysis = self.analyze_stock(symbol)
                if analysis['score'] > 0:
                    all_recommendations.append(analysis)
            
            # Sort by score in descending order
            sorted_recommendations = sorted(
                all_recommendations,
                key=lambda x: x['score'],
                reverse=True
            )
            
            # Get top N recommendations
            top_recommendations = sorted_recommendations[:top_n]
            
            # Add ranking and timestamp
            for rank, rec in enumerate(top_recommendations, 1):
                rec['rank'] = rank
                rec['timestamp'] = datetime.now().isoformat()
            
            return top_recommendations
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

    def generate_recommendation_report(self, recommendations: List[Dict]) -> str:
        """Generate a detailed recommendation report."""
        try:
            report = "Stock Recommendations Report\n"
            report += f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            for rec in recommendations:
                report += f"Rank {rec['rank']}: {rec['symbol']}\n"
                report += f"Overall Score: {rec['score']:.2f}\n"
                report += "Technical Indicators:\n"
                
                metrics = rec['metrics']
                report += f"- RSI: {metrics['rsi']:.2f}\n"
                report += f"- MACD: {metrics['macd']:.2f}\n"
                report += f"- Volatility: {metrics['volatility']:.2f}\n"
                report += f"- Volume Change: {metrics['volume_change']:.2%}\n"
                report += f"- Price Momentum: {metrics['price_momentum']:.2%}\n\n"
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating recommendation report: {e}")
            return "Error generating recommendation report"

    def save_recommendations(self, recommendations: List[Dict], filename: str = "recommendations.csv"):
        """Save recommendations to a CSV file."""
        try:
            df = pd.DataFrame(recommendations)
            output_path = PROCESSED_DATA_DIR / filename
            df.to_csv(output_path, index=False)
            logger.info(f"Recommendations saved to {output_path}")
        except Exception as e:
            logger.error(f"Error saving recommendations: {e}")
            raise

    def load_recommendations(self, filename: str = "recommendations.csv") -> List[Dict]:
        """Load recommendations from a CSV file."""
        try:
            input_path = PROCESSED_DATA_DIR / filename
            df = pd.read_csv(input_path)
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error loading recommendations: {e}")
            return []

    def get_historical_performance(self, symbol: str, lookback_days: int = 30) -> Dict:
        """Calculate historical performance metrics for a stock."""
        try:
            df = self.data_processor.load_data(symbol)
            
            # Calculate returns
            df['returns'] = df['close'].pct_change()
            
            # Get relevant period
            end_date = df['date'].max()
            start_date = end_date - timedelta(days=lookback_days)
            period_data = df[df['date'] >= start_date]
            
            return {
                'symbol': symbol,
                'period_return': period_data['returns'].sum(),
                'volatility': period_data['returns'].std(),
                'sharpe_ratio': period_data['returns'].mean() / period_data['returns'].std(),
                'max_drawdown': (period_data['close'] / period_data['close'].cummax() - 1).min(),
                'volume_trend': period_data['volume'].pct_change().mean()
            }
        except Exception as e:
            logger.error(f"Error calculating historical performance for {symbol}: {e}")
            return {}
