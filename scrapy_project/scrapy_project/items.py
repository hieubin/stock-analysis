import scrapy

class StockItem(scrapy.Item):
    id = scrapy.Field()
    ticker = scrapy.Field()
    isin = scrapy.Field()
    figi = scrapy.Field()
    company_name = scrapy.Field()
    registration_volume = scrapy.Field()
    float_volume = scrapy.Field()
    listing_date = scrapy.Field()

class ETFItem(scrapy.Item):
    id = scrapy.Field()
    index = scrapy.Field()
    index_name = scrapy.Field()
    code = scrapy.Field()
    isin = scrapy.Field()
    figi = scrapy.Field()
    fund_name = scrapy.Field()
    nav = scrapy.Field()
    shares = scrapy.Field()
    listing_date = scrapy.Field()

class WarrantItem(scrapy.Item):
    id = scrapy.Field()
    code = scrapy.Field()
    type = scrapy.Field()
    name = scrapy.Field()
    volume = scrapy.Field()
    isin = scrapy.Field()
    issuer = scrapy.Field()
    issuer_name = scrapy.Field()
    maturity = scrapy.Field()
