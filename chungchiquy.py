import scrapy
import json
from urllib.parse import urlencode

class HoseSpider(scrapy.Spider):
    name = "hose_spider"
    start_urls = [
        'https://www.hsx.vn/Modules/Listed/Web/ListInvCer',
    ]

    def __init__(self):
        self.cookies = {
            '_ga_3Z6T19EH14': 'GS1.1.1733960982.4.1.1733961119.0.0.0',
            '_ga': 'GA1.2.1682276058.1733323871',
            'TS016df111': '01343ddb6a28fb3c302e2cf136d0fd41c4da8ba4edfd821bd167407ff03bfee466143c039757218b935fb40565f1ff711ce239b9876ecdcad65a8d5a9162355d40b44448d1',
            'TS0d710d04027': '085cef26a9ab200077132199fe780dd403a05ed186bf9741a94f0cb9f17c5c82eefb790191792e70084a84aefa1130009637898f69a53d6a61323972a4afd289cf9e1507d0beafd22e96a833c5c279f7e03ae90e41698e9239b3a84550b822c4',
            'ASP.NET_SessionId': '5t2fba2g3m4tpn0j0z4g2gcl',
            '_gid': 'GA1.2.110392141.1733960983',
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Referer': 'https://www.hsx.vn/Modules/Listed/Web/InvCers/1408566917?fid=c2d60b07bd4341cd8bb3bfc12cbfe5b3',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        self.params = {
            '_search': 'false',
            'nd': '1733961119356',
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
                'ticker': item['cell'][1],
                'isin': item['cell'][2],
                'figi': item['cell'][3],
                'company_name': item['cell'][4],
                'registration_volume': item['cell'][5],
                'float_volume': item['cell'][6],
                'listing_date': item['cell'][7],
            }

        # Get the next page
        next_page = data['page'] + 1
        if next_page <= data['total']:
            self.params['page'] = str(next_page)
            params = urlencode(self.params)
            full_url = f"{self.start_urls[0]}?{params}"
            yield scrapy.Request(url=full_url, method='GET', headers=self.headers, cookies=self.cookies)