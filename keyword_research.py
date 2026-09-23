import random
import requests
from bs4 import BeautifulSoup

def get_high_search_product():
    """
    BDStall থেকে স্বয়ংক্রিয়ভাবে রিয়েল-টাইম প্রোডাক্টের টাইটেল, লিঙ্ক ও অফিশিয়াল ছবি নিয়ে আসে।
    """
    target_urls = [
        "https://www.bdstall.com/technology/",
        "https://www.bdstall.com/gadgets/",
        "https://www.bdstall.com/air-conditioner/"
    ]
    
    selected_url = random.choice(target_urls)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(selected_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # BDStall-এর প্রোডাক্ট লিস্ট কার্ড সিলেক্ট করা
            product_cards = soup.find_all('div', class_='ref_hot_deal_single') or soup.find_all('div', class_='product-list')

            scraped_products = []
            for card in product_cards:
                link_tag = card.find('a', href=True)
                img_tag = card.find('img')
                
                if link_tag and img_tag:
                    title = img_tag.get('alt', '').strip() or link_tag.text.strip()
                    product_url = link_tag['href']
                    if not product_url.startswith('http'):
                        product_url = "https://www.bdstall.com" + product_url

                    # আসল প্রোডাক্ট ইমেজের ইউআরএল এক্সট্রাক্ট করা
                    img_src = img_tag.get('src') or img_tag.get('data-src', '')
                    if img_src and not img_src.startswith('http'):
                        img_src = "https://www.bdstall.com" + img_src

                    if title and product_url and img_src:
                        scraped_products.append({
                            "title": f"{title} Review",
                            "url": product_url,
                            "image": img_src
                        })

            if scraped_products:
                return random.choice(scraped_products)

    except Exception as e:
        print(f"Scraping Error: {e}")

    # ব্যাকআপ প্রোডাক্ট (যদি স্ক্র্যাপিং ফেল করে)
    return {
        "title": "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds",
        "url": "https://www.bdstall.com/details/sony-wf-1000xm5-truly-wireless-noise-canceling-earbuds-102500/",
        "image": "https://www.bdstall.com/asset/product-image/product_102500.jpg"
    }
