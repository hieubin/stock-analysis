import scrapy
import json
from scrapy_project.items import ETFItem
from urllib.parse import urlencode

class ETFSpider(scrapy.Spider):
    name = "etf_list"
    base_url = 'https://www.hsx.vn/Modules/Listed/Web/EtfList'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.hsx.vn/Modules/Listed/Web/Etfs/123?fid=2d364da93f7f46af91f66f26f6ef50b9',
    }

    params = {
        'pageFieldName1': 'Code',
        'pageFieldValue1': '',
        'pageFieldOperator1': 'eq',
        'pageFieldName2': 'StartWith',
        'pageFieldValue2': '',
        'pageFieldOperator2': '',
        'pageCriteriaLength': '2',
        '_search': 'false',
        'nd': '1733971686913',
        'rows': '30',
        'page': '1',
        'sidx': 'id',
        'sord': 'desc',
    }

    def start_requests(self):
        yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)

    def parse(self, response):
        data = json.loads(response.body)
        for item in data.values():
            if isinstance(item, dict):
                etf_item = ETFItem()
                etf_item['id'] = item.get('id', '')
                etf_item['index'] = item['cell'][1]
                etf_item['index_name'] = item['cell'][2]
                etf_item['code'] = item['cell'][3]
                etf_item['isin'] = item['cell'][4]
                etf_item['figi'] = item['cell'][5]
                etf_item['fund_name'] = item['cell'][6]
                etf_item['nav'] = item['cell'][7].replace('.', '').replace(',', '')
                etf_item['shares'] = item['cell'][8].replace('.', '').replace(',', '')
                etf_item['listing_date'] = item['cell'][9]
                yield etf_item

        # Get the next page
        next_page = int(data['page']) + 1
        if next_page <= int(data['total']):
            self.params['page'] = str(next_page)
            yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)
