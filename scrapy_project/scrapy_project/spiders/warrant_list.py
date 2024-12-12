import requests

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

response = requests.get('https://www.hsx.vn/Modules/Listed/Web/CWList', params=params, headers=headers)

sample_result = """
{
	"0": {
		"id": 2063,
		"cell": [
			2063,
			"CMSN2401",
			"Call (Mua)",
			"Chứng quyền MSN-HSC-MET10",
			"7.000.000,00",
			"VN0CMSN24016",
			"MSN",
			"Công ty Cổ phần Chứng khoán Thành phố Hồ Chí Minh",
			"",
			"06/03/2025",
			""
		]
	}
}
"""