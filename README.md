# Bricolage Spider

## Project Description

This project contains a **Scrapy Spider** that scrapes all products from the **screwdrivers** category on the website [mr-bricolage.bg](https://mr-bricolage.bg). The main goal of this Spider is to collect important data for the products in this category, including:

- Product title
- Price
- Rating
- Images
- Technical specifications

## Project Structure

Description of the project structure:

- **spiders/spider.py**: The main file containing the logic of the Scrapy Spider.
- **settings.py**: Configuration settings for the Scrapy project.
- **tests/**: Tests for the project.
- **logs/**: Folder for logs from the Spider's execution.
- **results/**: Folder where the collected results are saved in JSON format.

## Installation

1. **Install dependencies:**

   To install all necessary libraries, use the following commands:

   ```bash
   pip install -r requirements.txt

   
## Setting up a virtual environment (optional):
To create a virtual environment, use the following commands:

```bash
python -m venv env
source env/bin/activate      # For Linux/MacOS
env\Scripts\Activate.bat     # For Windows
```

# Usage
## Starting the Spider:
To start the Spider and begin scraping the products, use the following command:

```bash 
scrapy crawl bricolage
```

This will start scraping all products from the "screwdrivers" category on the site and save the results in the results/ folder.


## Output Data:
The results will be saved in JSON format in the results/ directory. Each saved JSON file will contain the following data for each product:

``product_name``: Product title

``price``: Product price

``rating``: Product rating

``images``: Product images

``technical_specifications``: Product technical specifications

## Tests:
The project also includes test scripts that verify whether the extracted data is correct. To run the tests, use the command:

```bash
pytest
```

# Configuration
The Scrapy project settings are located in settings.py. You can modify the configuration for data processing and other parameters related to the Spider. For example, you can change the number of items per page or configure the logic for pausing between requests.

# Logs
During the execution of the Spider, all logs will be saved in the logs/ directory. This includes both execution information and any potential errors.
