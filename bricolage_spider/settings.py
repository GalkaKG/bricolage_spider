BOT_NAME = 'bricolage_spider'

SPIDER_MODULES = ['bricolage_spider.spiders']
NEWSPIDER_MODULE = 'bricolage_spider.spiders'

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)

ROBOTSTXT_OBEY = True

LOG_FILE = 'logs/scrapy_output.log'
LOG_LEVEL = 'INFO'

FEEDS = {
    'results/output.json': {
        'format': 'json',
        'encoding': 'utf8',
        'overwrite': True,
    },
}

ITEM_PIPELINES = {
    'bricolage_spider.pipelines.JsonWriterPipeline': 300,
}
