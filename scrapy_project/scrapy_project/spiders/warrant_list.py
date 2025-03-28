import scrapy
import json
from urllib.parse import urlencode
from scrapy_project.items import WarrantItem

class WarrantSpider(scrapy.Spider):
    name = "warrant_list"
    base_url = 'https://www.hsx.vn/Modules/Listed/Web/CWList'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.hsx.vn/Modules/Listed/Web/Cws?fid=2325165eee46463aa3d0d2bd68542844',
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
        'nd': '1733971302697',
        'rows': '50',
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
                warrant_item = WarrantItem()
                warrant_item['id'] = item['id']
                warrant_item['code'] = item['cell'][1]
                warrant_item['type'] = item['cell'][2]
                warrant_item['name'] = item['cell'][3]
                warrant_item['volume'] = item['cell'][4].replace('.', '').replace(',', '')
                warrant_item['isin'] = item['cell'][5]
                warrant_item['issuer'] = item['cell'][6]
                warrant_item['issuer_name'] = item['cell'][7]
                warrant_item['maturity'] = item['cell'][9]
                yield warrant_item

        # Get the next page
        next_page = int(data['page']) + 1
        if next_page <= int(data['total']):
            self.params['page'] = str(next_page)
            yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)
