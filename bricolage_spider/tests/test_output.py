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
