import scrapy
import json
from urllib.parse import urlencode

class BondSpider(scrapy.Spider):
    name = "bond_list"
    base_url = 'https://www.hsx.vn/Modules/Listed/Web/BondList'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.hsx.vn/Modules/Listed/Web/Bond/153?fid=1db6fa19ada84841a057fdae2ddc5906',
    }

    params = {
        "pageFieldName1": "BondTypes",
        "pageFieldValue1": "",
        "pageFieldOperator1": "",
        "pageFieldName2": "TypeId",
        "pageFieldValue2": "00000000-0000-0000-0000-000000000000",
        "pageFieldOperator2": "",
        "pageFieldName3": "Terms",
        "pageFieldValue3": "",
        "pageFieldOperator3": "",
        "pageFieldName4": "Term",
        "pageFieldValue4": "",
        "pageFieldOperator4": "",
        "pageCriteriaLength": "4",
        "_search": "false",
        "nd": '1733970344514',
        "rows": "30",
        "page": "1",
        "sidx": "id",
        "sord": "desc",
    }

    def start_requests(self):
        yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)

    def parse(self, response):
        data = json.loads(response.body)
        for item in data['rows']:
            yield {
                'id': item['id'],  # Extracting the ID
                'bond_ticker': item['cell'][1].strip(),  # Bond ticker from the cell array
                'issuer': item['cell'][2].strip(),        # Issuer from the cell array
                'listed_volume': item['cell'][3].replace('.', '').replace(',', ''),  # Clean listed volume
                'price': item['cell'][4].replace('.', '').replace(',', ''),  # Clean price
                'rate': item['cell'][5],                    # Rate from the cell array
                'maturity': item['cell'][6],                # Maturity from the cell array
                'listing_date': item['cell'][7],           # Listing date from the cell array
            }

        # Get the next page
        next_page = data['page'] + 1
        if next_page <= data['total']:
            self.params['page'] = str(next_page)
            yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)