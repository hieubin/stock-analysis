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
            '_ga_3Z6T19EH14': 'GS1.1.1733960982.4.1.1733961185.0.0.0',
            '_ga': 'GA1.2.1682276058.1733323871',
            'TS016df111': '01343ddb6a28fb3c302e2cf136d0fd41c4da8ba4edfd821bd167407ff03bfee466143c039757218b935fb40565f1ff711ce239b9876ecdcad65a8d5a9162355d40b44448d1',
            'TS0d710d04027': '085cef26a9ab2000e913755c91ff3eb0ad2c65be9559a1dd1dba9fd63f3382129f295a27c3e231a8089a5869331130007f96483c4b3aa8b3061729c1d832acf456ba8f92be94dd1f25ee201e32ebb4a42dd5265de19c1034d3ae4fa30c0a3236',
            'ASP.NET_SessionId': '5t2fba2g3m4tpn0j0z4g2gcl',
            '_gid': 'GA1.2.110392141.1733960983',
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
            'nd': '1733961185567',
            'rows': '30',
            'page': '1',
            'sidx': 'id',
            'sord': 'desc',
        }

    def start_requests(self):
        url = self.start_urls[0]
        params = urlencode(self.params)
        full_url = f"{url}?{params}"
        yield scrapy.Request(url=full_url, method='GET', headers=self.headers, cookies=self.cookies)

    def parse(self, response):
        data = json.loads(response.body)
        for item in data['rows']:
            yield {
                'bond_type': item['cell'][1],
                'type_id': item['cell'][2],
                'term': item['cell'][3],
                'bond_name': item['cell'][4],
                'issue_date': item['cell'][5],
                'maturity_date': item['cell'][6],
            }

        # Get the next page
        next_page = data['page'] + 1
        if next_page <= data['total']:
            self.params['page'] = str(next_page)
            params = urlencode(self.params)
            full_url = f"{self.start_urls[0]}?{params}"
            yield scrapy.Request(url=full_url, method='GET', headers=self.headers, cookies=self.cookies)