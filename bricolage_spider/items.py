import scrapy


class BricolageProductItem(scrapy.Item):
    product_name = scrapy.Field()
    price = scrapy.Field()
    rating = scrapy.Field()
    images = scrapy.Field()
    technical_specifications = scrapy.Field()


class StoreInfoItem(scrapy.Item):
    available_stores = scrapy.Field()
    store_with_most_stock = scrapy.Field()
