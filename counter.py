def count_products_in_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()  # Четем всички редове от файла

    product_count = 0

    # Преброяваме редовете, които започват с "Продукт:"
    for line in lines:
        if line.startswith("Продукт:"):
            product_count += 1

    return product_count

# Пример за използване
file_path = 'products_output.txt'  # Пътят към твоя текстов файл
total_products = count_products_in_file(file_path)
print(f"Общ брой продукти: {total_products}")
