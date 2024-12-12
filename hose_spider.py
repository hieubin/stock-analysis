import scrapy
import json
from urllib.parse import urlencode

class HoseSpider(scrapy.Spider):
    name = "hose_spider"
    start_urls = [
        'https://www.hsx.vn/Modules/Listed/Web/BondList',
    ]

    def __init__(self):
        self.cookies = {
            '_ga_3Z6T19EH14': 'GS1.1.1733751866.3.1.1733752535.0.0.0',
            '_ga': 'GA1.2.1682276058.1733323871',
            'TS016df111': '01343ddb6a3ab24416f0bf696a37c2da11b73f7be1dd72b25617d673c1cf041daa6715d1b031427653fdccede1655667f8fa3eb08e4da387e417f81aefeef7b322876773e3',
            'TS0d710d04027': '085cef26a9ab20008325aeb89d1d5adc6316bd0b8d796162e71586bd8d9a17bb177a6939860b1e3d08c3f11d30113000513ec5b64d9d2148644522189c48a6e9e3294db5e00e06aa0f111f50f615685c6cc6a5997a582e2e362d1aa5d8473129',
            '_gid': 'GA1.2.1371296529.1733751867',
            'ASP.NET_SessionId': 'cnikusfadwx043onvk2bjwqp',
            '_gat_gtag_UA_116051872_2': '1',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'https://www.hsx.vn/Modules/Listed/Web/Bond/153?fid=1db6fa19ada84841a057fdae2ddc5906',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        self.params = {
            'pageFieldName1': 'BondTypes',
            'pageFieldValue1': '',
            'pageFieldOperator1': '',
            'pageFieldName2': 'TypeId',
            'pageFieldValue2': '00000000-0000-0000-0000-000000000000',
            'pageFieldOperator2': '',
            'pageFieldName3': 'Terms',
            'pageFieldValue3': '',
            'pageFieldOperator3': '',
            'pageFieldName4': 'Term',
            'pageFieldValue4': '',
            'pageFieldOperator4': '',
            'pageCriteriaLength': '4',
            '_search': 'false',
            'nd': '1733752535901',
            'rows': '30',
            'page': '1',
            'sidx': 'id',
            'sord': 'desc',
        }

    def start_requests(self):
        url = self.start_urls[0]
        params = urlencode(self.params)
        full_url = f"{url}?{params}"
        yield scrapy.Request(url=full_url, method='GET', cookies=self.cookies, headers=self.headers)

    def parse(self, response):
        data = json.loads(response.body)
        for item in data['rows']:
            yield {
                # Extract the data you're interested in
                'bond_type': item['cell'][0],
                'type_id': item['cell'][1],
                'terms': item['cell'][2],
                'term': item['cell'][3],
                # Add more fields as needed
            }

        # Get the next page
        next_page = data['page'] + 1
        if next_page <= data['total']:
            self.params['page'] = str(next_page)
            params = urlencode(self.params)
            full_url = f"{self.start_urls[0]}?{params}"
            yield scrapy.Request(url=full_url, method='GET', cookies=self.cookies, headers=self.headers)