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


        except json.JSONDecodeError as e:
            logger.error(f"Грешка при парсване на JSON: {e}")
            logger.error(f"Пълен отговор: {response.text}")

            with open('logs/error_log.txt', 'w', encoding='utf-8') as f:
                f.write(f"JSON decode error: {str(e)}\n")
                f.write(f"Response headers: {dict(response.headers)}\n")
                f.write("Full response:\n")
                f.write(response.text)
