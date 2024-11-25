import scrapy
import json
from datetime import datetime
from urllib.parse import urljoin
from typing import Dict, Any

class HSXSpider(scrapy.Spider):
    name = 'hsx_spider'
    allowed_domains = ['hsx.vn']
    start_urls = ['https://www.hsx.vn/Modules/Listed/Web/StockList']

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0',
        'ROBOTSTXT_OBEY': True,
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 2,
    }

    def parse(self, response):
        stock_rows = response.css('table.table tbody tr')
        
        for row in stock_rows:
            symbol = row.css('td:nth-child(1)::text').get().strip()
            stock_url = urljoin(response.url, f'/Modules/Listed/Web/StockDetail/{symbol}')
            yield scrapy.Request(
                url=stock_url,
                callback=self.parse_stock_detail,
                meta={'symbol': symbol}
            )

    def parse_stock_detail(self, response):
        symbol = response.meta['symbol']
        
        # Extract basic information
        basic_info = {
            'symbol': symbol,
            'company_name': response.css('h1.title::text').get(),
            'market_cap': self._extract_market_cap(response),
            'volume': self._extract_volume(response),
            'price': self._extract_price(response),
            'timestamp': datetime.now().isoformat(),
        }

        # Get historical data URL
        historical_url = urljoin(
            response.url,
            f'/Modules/Listed/Web/HistoricalTradingData/{symbol}'
        )
        
        yield scrapy.Request(
            url=historical_url,
            callback=self.parse_historical_data,
            meta={'basic_info': basic_info}
        )

    def parse_historical_data(self, response):
        basic_info = response.meta['basic_info']
        
        # Extract historical trading data
        trading_rows = response.css('table.table tbody tr')
        historical_data = []
        
        for row in trading_rows:
            date_str = row.css('td:nth-child(1)::text').get().strip()
            try:
                trading_data = {
                    'date': datetime.strptime(date_str, '%Y-%m-%d').isoformat(),
                    'open': self._parse_float(row.css('td:nth-child(2)::text').get()),
                    'high': self._parse_float(row.css('td:nth-child(3)::text').get()),
                    'low': self._parse_float(row.css('td:nth-child(4)::text').get()),
                    'close': self._parse_float(row.css('td:nth-child(5)::text').get()),
                    'volume': self._parse_int(row.css('td:nth-child(6)::text').get()),
                }
                historical_data.append(trading_data)
            except (ValueError, AttributeError) as e:
                self.logger.error(f"Error parsing row for {basic_info['symbol']}: {e}")
                continue

        # Combine basic info with historical data
        yield {
            **basic_info,
            'historical_data': historical_data
        }

    @staticmethod
    def _extract_market_cap(response) -> float:
        market_cap_text = response.css('div.market-cap::text').get()
        return HSXSpider._parse_float(market_cap_text)

    @staticmethod
    def _extract_volume(response) -> int:
        volume_text = response.css('div.volume::text').get()
        return HSXSpider._parse_int(volume_text)

    @staticmethod
    def _extract_price(response) -> float:
        price_text = response.css('div.price::text').get()
        return HSXSpider._parse_float(price_text)

    @staticmethod
    def _parse_float(value: str) -> float:
        try:
            return float(value.replace(',', '').strip())
        except (ValueError, AttributeError):
            return 0.0

    @staticmethod
    def _parse_int(value: str) -> int:
        try:
            return int(value.replace(',', '').strip())
        except (ValueError, AttributeError):
            return 0
