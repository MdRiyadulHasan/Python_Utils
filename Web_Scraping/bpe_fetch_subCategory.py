import requests
from bs4 import BeautifulSoup
import json

import os, sys

# 1. Add project root (where manage.py lives) to sys.path
PROJECT_ROOT = r"E:\Web_Scrapping\ElementSearch"
sys.path.append(PROJECT_ROOT)

# 2. Tell Django where your settings are
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ElementSearch.settings")

# 3. Now you can setup Django
import django
django.setup()
from product.models import Category

def scrape_pump_categories(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    categories = []

    # Match the pump category items
    category_items = soup.select('ul.zoey-category-list > li.zoey-list-item')

    for item in category_items:
        # Extract anchor tag for URL and image
        anchor = item.find('a', class_='zoey-product-image')
        if not anchor:
            continue

        category_url = anchor.get('href', '').strip()
        image_style = anchor.get('style', '')
        image_url = ''
        if 'background-image:' in image_style:
            image_url = image_style.split('url(')[-1].split(')')[0].strip('"').strip()

        # Extract name
        title_tag = item.find('h3', class_='zoey-list-item-title')
        name = title_tag.get_text(strip=True) if title_tag else 'No Name'

        # Extract product count
        count_tag = item.find('div', class_='zoey-list-item-count')
        product_count = count_tag.get_text(strip=True) if count_tag else '0 products'

        categories.append({
            'name': name,
            'url': category_url,
            'image_url': image_url,
            'product_count': product_count
        })

    return categories

# Example usage
if __name__ == "__main__":
    get_category = Category.objects.filter(vendorTextId='bpe')
    if get_category:
        for category in get_category:
            print(category.categoryTite)
            print(category.categoryUrl)
            url = category.categoryUrl
            results = scrape_pump_categories(url)
            for cat in results:
                Category.objects.create(
                    vendorTextId = 'bpe',
                    vendorTitle = 'Burt Process Equipment',
                    categoryTextId = cat['name'].replace(' ', '-').lower(),
                    parentCategoryTextId = category.categoryTextId,
                    categoryTite = cat['name'],
                    categoryUrl = cat['url'],
                    categoryImageUrl = cat['image_url'],
                    productCount = int(cat['product_count'].split()[0]) if cat['product_count'].split()[0].isdigit() else 0
                    
                )
                print(f"Name: {cat['name']}")
                print(f"URL: {cat['url']}")
                print(f"Image: {cat['image_url']}")
                print(f"Products: {cat['product_count']}")
                print('---')
            
          