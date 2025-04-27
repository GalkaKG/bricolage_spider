import json

import scrapy
from bs4 import BeautifulSoup
from scrapy.utils.log import logger


class BricolageSpider(scrapy.Spider):
    name = 'bricolage'

    base_url = 'https://api.mr-bricolage.bg/occ/v2/bricolage-spa/categories/006003013'
    start_urls = [
        f'{base_url}/products/all?fields=FULL&pageSize=30&sort=relevance&query=&lang=bg&curr=BGN'
    ]

    def __init__(self):
        super().__init__()
        self.available_stores_text = []
        self.store_with_most_stock = []

    def start_requests(self):
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0',
        }
        yield scrapy.Request(url=self.start_urls[0], headers=headers, callback=self.parse)

    def parse(self, response):
        logger.info(f"Response sample: {response.text[:200]}...")

        try:
            data = json.loads(response.text)

            with open('results/parsed_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info("Успешно записан parsed_response.json")

            available_stores_text = ''
            available_stores = next(
                (facet for facet in data.get('facets', []) if facet.get('code') == 'availableInStores'), None)

            if available_stores:
                available_stores_list = []
                for store in available_stores.get('values', []):
                    store_name = store.get('name')
                    store_count = store.get('count')
                    available_stores_list.append(f"{store_name}: {store_count} налични продукта")

                available_stores_text = available_stores_list

            logger.info(f"Наличност по магазини:\n{available_stores_text}")

            store_with_most_stock = ''
            if available_stores and available_stores.get('values'):
                top_store = max(available_stores['values'], key=lambda x: x.get('count', 0))
                top_store_name = top_store.get('name')
                top_store_count = top_store.get('count')
                store_with_most_stock = f"{top_store_name} ({top_store_count} налични продукта)"

            max_count = max((store.get('count', 0) for store in available_stores.get('values', [])), default=0)

            top_stores = [
                f"{store.get('name')} ({store.get('count')} налични продукта)"
                for store in available_stores.get('values', [])
                if store.get('count') == max_count
            ]

            store_with_most_stock = top_stores

            logger.info(f"Магазин с най-много налични продукти: {store_with_most_stock}")

            for product in data.get('products', []):
                product_name = product.get('name')

                price = product.get('price', {}).get('formattedValue', '').replace('\xa0', '')

                rating = product.get('averageRating', {})
                images = [image.get('url') for image in product.get('images', [])]
                description_html = product.get('description', '')

                soup = BeautifulSoup(description_html, 'html.parser')

                technical_specifications = [
                    element.get_text(strip=True).replace('\xa0', ' ')
                    for element in soup.find_all(True)
                    if element.get_text(strip=True)
                ]

                known_brands = [
                    "BOSCH", "BLACK&DECKER", "BOSCH PROFESSIONAL", "DAEWOO", "DEWALT",
                    "EINHELL", "GREEN TOOLS", "HIKOKI", "HYUNDAI", "INVENTIV", "MAKITA",
                    "METABO", "NEXTOOL", "PROCRAFT", "RAIDER", "SKIL", "TOTAL", "TOTAL IND", "TOTAL INDUSTRIAL"
                ]

                found_brand = None
                for brand in known_brands:
                    if brand.lower() in product_name.lower():
                        found_brand = brand
                        break

                if not found_brand:
                    for spec in technical_specifications:
                        for brand in known_brands:
                            if brand.lower() in spec.lower():
                                found_brand = brand
                                break
                        if found_brand:
                            break

                if found_brand and found_brand.lower() not in product_name.lower():
                    product_name = f"{found_brand} {product_name}"

                logger.info(f"Продукт: {product_name}")
                logger.info(f"Цена: {price}")
                logger.info(f"Рейтинг: {rating}")
                logger.info(f"Снимки: {', '.join(images)}")
                logger.info(f"Технически характеристики: {', '.join(technical_specifications)}")
                logger.info("-" * 50)

                yield {
                    'product_name': product_name,
                    'price': price,
                    'rating': rating,
                    'images': images,
                    'technical_specifications': technical_specifications,
                }



            pagination = data.get('pagination', {})
            current_page = pagination.get('currentPage', 0)
            total_pages = pagination.get('totalPages', 0)

            if current_page < total_pages - 1:
                next_page = current_page + 1
                next_page_url = f"{self.base_url}/products/all?fields=FULL&pageSize=30&sort=relevance&query=&lang=bg" \
                                f"&curr=BGN&currentPage={next_page} "
                yield scrapy.Request(url=next_page_url,
                                     headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'},
                                     callback=self.parse)

            # yield {
            #     'stores_info': {
            #         'available_stores': available_stores_text,
            #         'store_with_most_stock': store_with_most_stock,
            #     }
            # }

            self.available_stores_text = available_stores_text
            self.store_with_most_stock = top_stores


        except json.JSONDecodeError as e:
            logger.error(f"Грешка при парсване на JSON: {e}")
            logger.error(f"Пълен отговор: {response.text}")

            with open('logs/error_log.txt', 'w', encoding='utf-8') as f:
                f.write(f"JSON decode error: {str(e)}\n")
                f.write(f"Response headers: {dict(response.headers)}\n")
                f.write("Full response:\n")
                f.write(response.text)

    def closed(self, reason):
        output = {
            'stores_info': {
                'available_stores': self.available_stores_text,
                'store_with_most_stock': self.store_with_most_stock,
            }
        }
        with open('results/stores_info.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info("Успешно записан stores_info.json")
