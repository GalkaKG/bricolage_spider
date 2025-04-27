import json
import os


def test_scrapy_output_count():
    output_file = 'results/output.json'
    expected_count = 182

    assert os.path.exists(output_file), f"Файлът {output_file} не съществува!"

    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert isinstance(data, list), "Output JSON не е списък!"

    assert len(data) == expected_count, f"Очаквани {expected_count} елемента, но намерени {len(data)}"


def test_product_price():
    output_file = 'results/output.json'

    assert os.path.exists(output_file), f"Файлът {output_file} не съществува!"

    with open(output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for product in data:
        price = product.get('price')
        assert price is not None, f"Продуктът без цена: {product['product_name']}"

        price_cleaned = price.replace('\xa0', '').replace('лв.', '').replace('BGN', '').strip()
        try:
            price_value = float(price_cleaned.replace(',', '.'))
        except ValueError:
            assert False, f"Цена не може да бъде преобразувана в число за продукт: {product['product_name']}"

        assert price_value > 0, f"Невалидна цена за продукт: {product['product_name']}"
