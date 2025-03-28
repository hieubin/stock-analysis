import pymongo
from scrapy_project.utils import generate_id

class MongoPipeline:
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        item['_id'] = generate_id(item)
        existing_item = collection.find_one({'_id': item['_id']})
        if existing_item:
            if existing_item != item:
                collection.update_one({'_id': item['_id']}, {'$set': item})
        else:
            collection.insert_one(dict(item))
        return item
