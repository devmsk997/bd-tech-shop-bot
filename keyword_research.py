import random
import requests
from bs4 import BeautifulSoup

def get_high_search_product():
    """
    বিডি স্টলের (BDStall) সমস্ত টেক ক্যাটাগরি (টপ সেলস + অন্যান্য গ্যাজেট) থেকে স্বয়ংক্রিয়ভাবে অরিজিনাল ডাটা স্ক্র্যাপ করে।
    """
    # বিডি স্টলের সম্পূর্ণ টেকনোলজি ক্যাটাগরি তালিকা (টপ সেলস + অল টেক)
    target_urls = [
        # দ্রুত বিক্রি ও বেশি সার্চ হওয়া ক্যাটাগরি
        "https://www.bdstall.com/mobile-phone/",
        "https://www.bdstall.com/gadgets/",
        "https://www.bdstall.com/smart-watch/",
        "https://www.bdstall.com/sound-system/",
        "https://www.bdstall.com/laptop-computer/",
        "https://www.bdstall.com/networking-router/",
        "https://www.bdstall.com/cc-camera/",
        "https://www.bdstall.com/gaming-accessories/",
        
        # অন্যান্য সব টেক ও অফিস ক্যাটাগরি
        "https://www.bdstall.com/technology/",
        "https://www.bdstall.com/camera/",
        "https://www.bdstall.com/television/",
        "https://www.bdstall.com/desktop-computer/",
        "https://www.bdstall.com/printer/",
        "https://www.bdstall.com/projector/",
        "https://www.bdstall.com/ips-ups/",
        "https://www.bdstall.com/computer-accessories/",
        "https://www.bdstall.com/scanner/",
        "https://www.bdstall.com/server/",
        "https://www.bdstall.com/intercom/"
    ]
    
    selected_url = random.choice(target_urls)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(selected_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # প্রোডাক্ট কার্ড সিলেক্ট করা
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

                    # অফিশিয়াল অরিজিনাল ইমেজের ইউআরএল এক্সট্র্যাক্ট করা
                    img_src = img_tag.get('src') or img_tag.get('data-src', '')
                    if img_src and not img_src.startswith('http'):
                        img_src = "https://www.bdstall.com" + img_src

                    if title and product_url and img_src:
                        scraped_products.append({
                            "title": f"{title} Price in Bangladesh & Review 2026",
                            "url": product_url,
                            "image": img_src
                        })

            if scraped_products:
                return random.choice(scraped_products)

    except Exception as e:
        print(f"Scraping Error: {e}")

    # ব্যাকআপ হাই-ডিমান্ড প্রোডাক্ট (যদি স্ক্র্যাপিং ফেল করে)
    return {
        "title": "Sony WF-1000XM5 Truly Wireless Noise Canceling Earbuds Price in Bangladesh 2026",
        "url": "https://www.bdstall.com/details/sony-wf-1000xm5-truly-wireless-noise-canceling-earbuds-102500/",
        "image": "https://www.bdstall.com/asset/product-image/product_102500.jpg"
    }
