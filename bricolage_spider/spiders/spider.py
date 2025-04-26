# import scrapy
# from urllib.parse import urljoin
#
#
# class BricolageSpider(scrapy.Spider):
#     name = 'screwdrivers'
#     start_urls = ['https://mr-bricolage.bg/instrumenti/elektroprenosimi-instrumenti/vintoverti/c/006003013']
#
#     custom_settings = {
#         'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#         'FEED_EXPORT_ENCODING': 'utf-8',
#     }
#
#     def parse(self, response):
#         # Extract product items
#         products = response.css('div.plp-product')
#
#         for product in products:
#             yield {
#                 'name': product.css('cx-media[title]::attr(title)').get(),
#                 'url': urljoin(response.url, product.css('a::attr(href)').get()),
#                 'image_url': product.css('cx-media img::attr(src)').get(),
#                 'price': self.clean_price(product.css('span.price::text').get()),
#                 'discount': product.css('span.sale-percentage-text::text').get(),
#                 'brand': product.css('div.product__brand::text').get(),
#                 'is_promo': bool(product.css('div.sale-badge.TOP_RIGHT').get()),
#             }
#
#         # Handle pagination if needed
#         next_page = response.css('a.next-page::attr(href)').get()
#         if next_page:
#             yield response.follow(next_page, self.parse)
#
#     def clean_price(self, price_str):
#         if price_str:
#             return price_str.replace('лв.', '').replace(',', '.').strip()
#         return None



import json
import scrapy
from scrapy.utils.log import logger
from bs4 import BeautifulSoup  # Използваме BeautifulSoup за да парсваме HTML

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
        # Логваме първите 200 символа от отговора за дебъг
        logger.info(f"Response sample: {response.text[:200]}...")

        try:
            data = json.loads(response.text)

            # Записваме парснатия JSON във файл
            with open('parsed_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info("Успешно записан parsed_response.json")

            # Преработваме данните и извличаме конкретни елементи
            for product in data.get('products', []):  # Предполага се, че продуктите са в 'products'
                product_name = product.get('name')  # Заглавие

                # Премахваме &nbsp; от цената
                price = product.get('price', {}).get('formattedValue', '').replace('\xa0', '')  # Цена

                rating = product.get('averageRating', {}) # Рейтинг
                images = [image.get('url') for image in product.get('images', [])]  # Снимки
                description_html = product.get('description', '')  # Технически характеристики (HTML формат)

                # Извличаме всички текстови данни от HTML чрез BeautifulSoup
                soup = BeautifulSoup(description_html, 'html.parser')
                technical_specifications = []

                # Извличаме текст от всички тагове (не само <li>) и премахваме &nbsp; символите
                for element in soup.find_all(True):  # "True" извлича всички тагове
                    text = element.get_text(strip=True)
                    # Премахваме &nbsp; символи и други невалидни символи
                    clean_text = text.replace('\xa0', ' ')  # Замяна на &nbsp; с нормален интервал
                    if clean_text:  # Ако има текст в елемента
                        technical_specifications.append(clean_text)

                # Логваме или записваме данните
                logger.info(f"Продукт: {product_name}")
                logger.info(f"Цена: {price}")
                logger.info(f"Рейтинг: {rating}")
                logger.info(f"Снимки: {', '.join(images)}")
                logger.info(f"Технически характеристики: {', '.join(technical_specifications)}")
                logger.info("-" * 50)

                # Можеш да запишеш извлечените данни във файл или да ги обработиш по друг начин
                with open('products_output.txt', 'a', encoding='utf-8') as f:
                    f.write(f"Продукт: {product_name}\n")
                    f.write(f"Цена: {price}\n")
                    f.write(f"Рейтинг: {rating}\n")
                    f.write(f"Снимки: {', '.join(images)}\n")
                    f.write(f"Технически характеристики: {', '.join(technical_specifications)}\n")
                    f.write("-" * 50 + "\n")

            # Проверяваме дали има следваща страница
            pagination = data.get('pagination', {})
            current_page = pagination.get('currentPage', 0)
            total_pages = pagination.get('totalPages', 0)

            # Ако има следваща страница, извикваме parse за нея
            if current_page < total_pages - 1:  # Проверяваме дали не сме стигнали до последната страница
                next_page = current_page + 1
                next_page_url = f"{self.base_url}/products/all?fields=FULL&pageSize=30&sort=relevance&query=&lang=bg&curr=BGN&currentPage={next_page}"
                yield scrapy.Request(url=next_page_url,
                                     headers={'Accept': 'application/json', 'User-Agent': 'Mozilla/5.0'},
                                     callback=self.parse)


        except json.JSONDecodeError as e:
            logger.error(f"Грешка при парсване на JSON: {e}")
            logger.error(f"Пълен отговор: {response.text}")

            # Записваме грешката във файл
            with open('error_log.txt', 'w', encoding='utf-8') as f:
                f.write(f"JSON decode error: {str(e)}\n")
                f.write(f"Response headers: {dict(response.headers)}\n")
                f.write("Full response:\n")
                f.write(response.text)
