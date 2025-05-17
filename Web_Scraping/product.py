import requests
from bs4 import BeautifulSoup

def scrape_product_details(category_url):
    try:
        response = requests.get(category_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the category page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    products = []

    product_items = soup.select('li[itemtype="http://schema.org/ListItem"]')

    for item in product_items:
        # Extract product information
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
        image_tag = item.select_one('a.zoey-product-image')
        image_url = ''
        if image_tag and 'background-image:' in image_tag.get('style', ''):
            style_content = image_tag['style']
            full_url = style_content.split('url(')[-1].split(')')[0].strip().strip('"').strip("'")
            
            # Get the actual image URL after the CDN part
            if 'https://' in full_url:
                image_url = full_url.split('https://')[-1]
                image_url = 'https://' + image_url  # Re-add the protocol

       

        products.append({
            'name': name_tag['content'] if name_tag else '',
            'sku': sku_tag['content'] if sku_tag else '',
            'url': url_tag['content'] if url_tag else '',
            'brand': brand_tag['content'] if brand_tag else '',
            'stock_status': stock_tag.text.strip() if stock_tag else '',
            'regular_price': regular_price_tag.text.strip() if regular_price_tag else '',
            'sale_price': sale_price_tag.text.strip() if sale_price_tag else '',
            'image_url': image_url  # Include the image URL
        })

    return products

# Example usage
if __name__ == "__main__":
    category_url = "https://burtprocess.com/fluid-handling/pumps/centrifugal-pumps"  
    products = scrape_product_details(category_url)

    if not products:
        print("No products found or there was an error scraping the products.")
    else:
        print(f"Found {len(products)} products in this category:\n")
        for i, product in enumerate(products, 1):
            print(f"Product {i}")
            for key, value in product.items():
                print(f"{key}: {value}")
            print("-" * 40)
