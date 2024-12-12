import requests

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

response = requests.get('https://www.hsx.vn/Modules/Listed/Web/EtfList', params=params, headers=headers)

sample_result = """
{
	"0": {
		"id": 578,
		"cell": [
			578,
			"1",
			"VN30 Index",
			"E1VFVN30",
			"VN0E1VFVN306",
			"BBG006Y04478",
			"Quỹ ETF DCVFMVN30",
			"293.000.000,00",
			"293.000.000,00",
			"29/09/2014"
		]
	}
}
"""