import json


class JsonWriterPipeline:
    def __init__(self):
        self.first_item = None
        self.products_file = None

    def open_spider(self, spider):
        self.products_file = open('results/output.json', 'w', encoding='utf-8')
        self.products_file.write("") 
        self.first_item = True

    def close_spider(self, spider):
        if hasattr(spider, 'stores_info'):
            with open('results/stores_info.json', 'w', encoding='utf-8') as f:
                json.dump(spider.stores_info, f, ensure_ascii=False, indent=2)
        self.products_file.close()

    def process_item(self, item, spider):
        if isinstance(item, dict) and 'product_name' in item:
            item_data = json.dumps(dict(item), ensure_ascii=False)
            if self.first_item:
                self.products_file.write(item_data)
                self.first_item = False
            else:
                self.products_file.write("\n" + item_data)
        return item
