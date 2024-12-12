import scrapy
import json
from urllib.parse import urlencode

class CertificateSpider(scrapy.Spider):
    name = "certificate_list"
    base_url = 'https://www.hsx.vn/Modules/Listed/Web/ListInvCer'
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.hsx.vn/Modules/Listed/Web/InvCers/1408566917?fid=c2d60b07bd4341cd8bb3bfc12cbfe5b3',
    }

    params = {
        '_search': 'false',
        'nd': '1733970890443',
        'rows': '30',
        'page': '1',
        'sidx': 'id',
        'sord': 'desc',
    }


    def start_requests(self):
        yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)

    def parse(self, response):
        data = json.loads(response.body)
        for item in data['rows']:
            yield {
                'id': item['id'],  # Extracting the ID
                'ticker': item['cell'][1].strip(),  # Ticker from the cell array
                'fund_name': item['cell'][2].strip(),
                'fund_management_name': item['cell'][3].strip(),
                'registration_volume': item['cell'][4].replace('.', '').replace(',', ''),  # Clean volume
                'listing_date': item['cell'][5],  # Listing date from the cell array
            }

        # Get the next page
        next_page = data['page'] + 1
        if next_page <= data['total']:
            self.params['page'] = str(next_page)
            yield scrapy.Request(url=f"{self.base_url}?{urlencode(self.params)}", headers=self.headers)