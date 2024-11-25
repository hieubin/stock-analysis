# Stock Price Analysis and Recommendation System

## Overview
A comprehensive stock analysis system that scrapes, processes, and analyzes stock data from the Ho Chi Minh Stock Exchange (HSX.VN) to generate investment recommendations. The system combines web scraping, data processing, and machine learning to identify promising investment opportunities.

## Features
- **Automated Data Collection**: Scrapes real-time and historical stock data from HSX.VN
- **Advanced Data Processing**: Utilizes Python libraries for cleaning and analyzing financial data
- **Machine Learning Integration**: Implements predictive models for stock performance analysis
- **Dual Database System**: Efficiently manages data using both MongoDB and SQLite
- **Top 10 Stock Recommendations**: Generates investment suggestions based on multiple criteria

## Technology Stack
- **Web Scraping**: Scrapy
- **Data Processing**: Python, Pandas
- **Machine Learning**: Scikit-learn
- **Databases**: 
  - MongoDB (Large-scale data storage)
  - SQLite (Relational data operations)
- **Analysis Tools**: NumPy, Matplotlib

## Project Structure
```
Stock-Price-Analysis-Recommendation-System/
├── config/
│   ├── config.yaml           # Central configuration file
│   ├── logging_config.yaml   # Logging settings
│   └── database_config.yaml  # Database connection settings
├── data/
│   ├── raw/                 # Raw stock data files (CSV, JSON, etc.)
│   ├── processed/           # Cleaned and processed data files
│   └── database/           # Database files (SQLite, MongoDB dumps)
├── scrapy_project/         # Scrapy project for scraping stock prices
│   ├── stock_scraper/
│   │   ├── spiders/        # Spider files to scrape HSX.VN stock data
│   │   ├── items.py        # Data models for scraped items
│   │   ├── pipelines.py    # Data pipelines for cleaning and storing data
│   │   └── settings.py     # Scrapy project settings
├── src/                    # Main Python scripts for analysis and recommendation
│   ├── __init__.py
│   ├── constants.py        # Project constants
│   ├── data_processing.py  # Data cleaning and preprocessing
│   ├── exceptions.py       # Custom exceptions
│   ├── market_indicators.py # Technical indicators
│   ├── portfolio_optimizer.py # Portfolio optimization
│   ├── recommendation.py   # Stock recommendation system logic
│   ├── risk_analysis.py    # Risk metrics
│   ├── stock_analysis.py   # Stock analysis and performance metrics
│   └── visualization.py    # Plotting utilities
├── notebooks/             # Jupyter notebooks for exploration and analysis
│   └── stock_analysis_notebook.ipynb
├── models/               # Trained models
│   └── recommendation_model.pkl
├── tests/
│   ├── unit/
│   │   ├── test_data_processing.py
│   │   ├── test_recommendation.py
│   │   └── test_stock_analysis.py
│   ├── integration/
│   │   └── test_full_pipeline.py
│   └── conftest.py
├── utils/
│   ├── db_utils.py       # Database utilities
│   ├── logger.py         # Logging setup
│   ├── validators.py     # Data validation
│   └── metrics.py        # Custom performance metrics
├── scripts/
│   ├── setup_database.py      # Database initialization
│   ├── backup_data.py         # Backup utilities
│   ├── download_historical.py  # Initial data download
│   └── scheduled_updates.py    # Cron job scripts
├── web/                  # Optional web interface
│   ├── templates/
│   ├── static/
│   └── app.py
├── docs/
│   ├── api/              # API documentation
│   ├── database_schema/  # Database design docs
│   ├── analysis_methodology.md
│   └── deployment_guide.md
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .flaskenv             # Flask configurations
├── .pre-commit-config.yaml
├── setup.cfg             # Linting and formatting configs
├── pyproject.toml
├── Makefile             # Common commands
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation

### Prerequisites
```bash
# Python 3.8 or higher
python -m pip install --upgrade pip
```

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/stock-analysis-system.git
cd stock-analysis-system
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up configuration:
```bash
cp .env.example .env
# Update .env with your configuration
```

5. Initialize databases:
```bash
python scripts/setup_database.py
```

## Usage

### 1. Data Collection
```bash
# Start the Scrapy crawler
cd scrapy_project
scrapy crawl stock_prices
```

### 2. Data Processing
```bash
python src/data_processing.py
```

### 3. Generate Recommendations
```bash
python src/recommendation.py
```

### 4. Run Web Interface (Optional)
```bash
python web/app.py
```

## Data Flow
1. **Data Collection**: Scrapy crawlers collect stock data from HSX.VN
2. **Storage**: Raw data is stored in MongoDB collections
3. **Processing**: Data is cleaned and processed using Pandas
4. **Analysis**: Scikit-learn models analyze stock performance
5. **Results**: Top recommendations are stored in SQLite for quick access

## Analysis Criteria
The system evaluates stocks based on:
- Historical price trends
- Trading volume patterns
- Technical indicators (RSI, MACD, Moving Averages)
- Market capitalization
- Industry performance comparison
- Volatility metrics

## Database Schema

### MongoDB Collections
- **raw_stock_data**
  - timestamp
  - symbol
  - price
  - volume
  - market_cap
  - additional_metrics

### SQLite Tables
- **recommendations**
  - id
  - symbol
  - rank
  - score
  - timestamp
  - rationale

## Development

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test suite
python -m pytest tests/unit/test_recommendation.py
```

### Code Quality
```bash
# Run pre-commit hooks
pre-commit run --all-files

# Run linting
flake8 src tests

# Run type checking
mypy src
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments
- HSX.VN for providing stock market data
- Contributors and maintainers of the open-source libraries used in this project

## Contact
Project Link: [https://github.com/yourusername/stock-analysis-system](https://github.com/yourusername/stock-analysis-system)

## Disclaimer
This software is for educational and research purposes only. Do not use it as financial advice. Always do your own research before making investment decisions.
