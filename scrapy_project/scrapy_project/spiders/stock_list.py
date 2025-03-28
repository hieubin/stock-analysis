import scrapy
import json
from urllib.parse import urlencode
from scrapy_project.items import StockItem

class StockSpider(scrapy.Spider):
    name = "stock_list"
    base_url = 'https://www.hsx.vn/Modules/Listed/Web/SymbolList'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.hsx.vn/Modules/Listed/Web/Symbols?fid=9ac914fbe9434adca2801e30593d0ae2',
    }

    params = {
        'pageFieldName1': 'Code',
        'pageFieldValue1': '',
        'pageFieldOperator1': 'eq',
        'pageFieldName2': 'Sectors',
        'pageFieldValue2': '',
        'pageFieldOperator2': '',
        'pageFieldName3': 'Sector',
        'pageFieldValue3': '00000000-0000-0000-0000-000000000000',
        'pageFieldOperator3': '',
        'pageFieldName4': 'StartWith',
        'pageFieldValue4': '',
        'pageFieldOperator4': '',
        'pageCriteriaLength': '4',
        '_search': 'false',
        'nd': '1733969654447',
        'rows': '200',
        'page': '1',
        'sidx': 'id',
        'sord': 'desc',
    }


    def start_requests(self):
        yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)

    def parse(self, response):
        data = json.loads(response.body)
        for item in data['rows']:
            stock_item = StockItem()
            stock_item['id'] = item['id']
            stock_item['ticker'] = item['cell'][1]
            stock_item['isin'] = item['cell'][2]
            stock_item['figi'] = item['cell'][3]
            stock_item['company_name'] = item['cell'][4]
            stock_item['registration_volume'] = item['cell'][5].replace('.', '').replace(',', '')
            stock_item['float_volume'] = item['cell'][6].replace('.', '').replace(',', '')
            stock_item['listing_date'] = item['cell'][7]
            yield stock_item

        # Get the next page
        next_page = data['page'] + 1
        if next_page <= data['total']:
            self.params['page'] = str(next_page)
            yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)
