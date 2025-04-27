import json
import scrapy
from bs4 import BeautifulSoup
from scrapy.utils.log import logger
from ..items import BricolageProductItem, StoreInfoItem


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
        logger.info(f"Изпращане на заявка към: {self.start_urls[0]}")
        yield scrapy.Request(url=self.start_urls[0], headers=headers, callback=self.parse)

    def parse(self, response):
        logger.info(f"Обработен отговор от {response.url[:100]}... Първи 200 символа: {response.text[:200]}")

        try:
            data = json.loads(response.text)
            logger.info("Парсването на JSON е успешно.")

            self.parse_stores_info(data)

            for product in data.get('products', []):
                logger.info(f"Обработване на продукт: {product.get('name', 'Няма име')}")
                yield self.parse_product(product)

            pagination = data.get('pagination', {})
            current_page = pagination.get('currentPage', 0)
            total_pages = pagination.get('totalPages', 0)
            logger.info(f"Текуща страница: {current_page}, Общо страници: {total_pages}")

            if current_page < total_pages - 1:
                next_page = current_page + 1
                next_page_url = f"{self.base_url}/products/all?fields=FULL&pageSize=30&sort=relevance&query=&lang=bg&curr=BGN&currentPage={next_page}"
                logger.info(f"Преминаване към следваща страница: {next_page_url}")
                yield scrapy.Request(url=next_page_url,
                                     headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'},
                                     callback=self.parse)

        except json.JSONDecodeError as e:
            logger.error(f"Грешка при JSON парсинг: {e}")
            self.save_error(response)

    def parse_stores_info(self, data):
        available_stores = next(
            (facet for facet in data.get('facets', []) if facet.get('code') == 'availableInStores'), None)

        if available_stores:
            self.available_stores_text = [
                f"{store.get('name')}: {store.get('count')} налични продукта"
                for store in available_stores.get('values', [])
            ]
            logger.info(f"Налични магазини: {self.available_stores_text}")

            max_count = max((store.get('count', 0) for store in available_stores.get('values', [])), default=0)
            self.store_with_most_stock = [
                f"{store.get('name')} ({store.get('count')} налични продукта)"
                for store in available_stores.get('values', [])
                if store.get('count') == max_count
            ]
            logger.info(f"Магазин с най-много налични продукти: {self.store_with_most_stock}")

        self.stores_info = {
            'available_stores': self.available_stores_text,
            'store_with_most_stock': self.store_with_most_stock,
        }

    def parse_product(self, product):
        name = product.get('name', '').strip()

        price_raw = product.get('price', {}).get('formattedValue', '')
        price_cleaned = price_raw.replace('\xa0', '').replace('лв.', '').replace('BGN', '').strip()
        try:
            price_value = float(price_cleaned.replace(',', '.'))
            price = f"{price_value} лв."
        except ValueError:
            price = None

        rating = product.get('averageRating')
        if rating is None:
            rating = 'Няма'

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
            if brand.lower() in name.lower():
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

        if found_brand and found_brand.lower() not in name.lower():
            name = f"{found_brand} {name}"

        logger.info(f"Продуктът {name} ще бъде записан с цена: {price} и рейтинг: {rating}")
        return BricolageProductItem(
            product_name=name,
            price=price,
            rating=rating,
            images=images,
            technical_specifications=technical_specifications
        )

    def save_error(self, response):
        with open('logs/error_log.txt', 'w', encoding='utf-8') as f:
            f.write(f"Response error:\n{response.text}\n")
        logger.error(f"Записана е грешка в лог файла: {response.url[:100]}")
