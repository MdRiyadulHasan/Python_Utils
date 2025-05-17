import requests
from bs4 import BeautifulSoup
import json
import time

def get_product_description(product_url):
    """Fetches the product detail page and extracts the description."""
    try:
        response = requests.get(product_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        desc_tag = soup.select_one('[itemprop="description"]')
        return desc_tag.text.strip() if desc_tag else ''
    except Exception as e:
        print(f"Error fetching description from {product_url}: {e}")
        return ''

def scrape_all_products(category_url, max_pages=200):
    """Scrapes all products from paginated category pages."""
    products = []
    page = 1

    while page <= max_pages:
        paged_url = f"{category_url}?p={page}"
        print(f"Scraping page {page}: {paged_url}")

        try:
            response = requests.get(paged_url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        product_items = soup.select('li[itemtype="http://schema.org/ListItem"]')

        if not product_items:
            print("No more products found.")
            break

        for item in product_items:
            product_info = item.select_one('[itemtype="http://schema.org/Product"]')
            if not product_info:
                continue

            name_tag = product_info.select_one('[itemprop="name"]')
            sku_tag = product_info.select_one('[itemprop="sku"]')
            url_tag = product_info.select_one('[itemprop="url"]')
            brand_tag = product_info.select_one('[itemprop="brand"]')
            stock_tag = item.select_one('.category_stock_status .zoey-product-list-attribute-value')
            regular_price_tag = item.select_one('.old-price .price')
            sale_price_tag = item.select_one('.special-price .price')

            # Extract product image
            image_tag = item.select_one('a.zoey-product-image')
            image_url = ''
            if image_tag and 'background-image:' in image_tag.get('style', ''):
                style_content = image_tag['style']
                full_url = style_content.split('url(')[-1].split(')')[0].strip().strip('"').strip("'")
                if 'https://' in full_url:
                    image_url = 'https://' + full_url.split('https://')[-1]

            product_url = url_tag['content'] if url_tag else ''
            description = get_product_description(product_url) if product_url else ''

            products.append({
                'name': name_tag['content'] if name_tag else '',
                'sku': sku_tag['content'] if sku_tag else '',
                'url': product_url,
                'brand': brand_tag['content'] if brand_tag else '',
                'stock_status': stock_tag.text.strip() if stock_tag else '',
                'regular_price': regular_price_tag.text.strip() if regular_price_tag else '',
                'sale_price': sale_price_tag.text.strip() if sale_price_tag else '',
                'image_url': image_url,
                'description': description
            })

            time.sleep(0.25)  # Be polite to the server

        page += 1

    return products

# Run scraper and save output to JSON
if __name__ == "__main__":
    category_url = "https://burtprocess.com/fluid-handling/pumps/sump-pump"
    all_products = scrape_all_products(category_url)

    print(f"\nTotal products scraped: {len(all_products)}")

    with open("products_output.json", "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=4, ensure_ascii=False)

    print("✅ Product data saved to 'products_output.json'")