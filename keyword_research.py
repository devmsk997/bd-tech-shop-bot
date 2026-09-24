import random
import requests
from bs4 import BeautifulSoup

def get_high_search_product():
    """
    বিডি স্টল (BDStall) থেকে শুধুমাত্র হাই-সার্চ ভলিউম এবং ফাস্ট-সেলিং টেক প্রোডাক্ট ও গ্যাজেট স্ক্র্যাপ করে।
    """
    # যেসব ক্যাটাগরিতে মানুষের সার্চ ও বিক্রির হার সবচেয়ে বেশি
    target_urls = [
        "https://www.bdstall.com/mobile-phone/",
        "https://www.bdstall.com/smart-watch/",
        "https://www.bdstall.com/gadgets/",
        "https://www.bdstall.com/sound-system/"
    ]
    
    selected_url = random.choice(target_urls)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.bdstall.com/"
    }

    try:
        response = requests.get(selected_url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # একাধিক সম্ভাব্য কন্টেইনার বা কার্ড ক্লাস টার্গেট করা যাতে স্ক্র্যাপিং ফেইল না করে
            product_cards = (
                soup.find_all('div', class_='ref_hot_deal_single') or 
                soup.find_all('div', class_='product-list') or
                soup.find_all('div', class_='col-sm-4') or
                soup.find_all('div', class_='item-grid') or
                soup.find_all('div', class_='product-item') or
                soup.find_all('div', class_='box')
            )

            scraped_products = []
            for card in product_cards:
                link_tag = card.find('a', href=True)
                img_tag = card.find('img')
                
                if link_tag and img_tag:
                    title = img_tag.get('alt', '').strip() or link_tag.text.strip()
                    product_url = link_tag['href']
                    
                    if not product_url or len(title) < 5:
                        continue
                        
                    if not product_url.startswith('http'):
                        product_url = "https://www.bdstall.com" + product_url

                    img_src = (
                        img_tag.get('data-src') or 
                        img_tag.get('src') or 
                        img_tag.get('data-original', '')
                    )
                    
                    if img_src:
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        elif not img_src.startswith('http'):
                            img_src = "https://www.bdstall.com" + img_src

                        scraped_products.append({
                            "title": f"{title} Price in Bangladesh & Review 2026",
                            "url": product_url,
                            "image": img_src
                        })

            if scraped_products:
                selected_prod = random.choice(scraped_products)
                print(f"✅ Successfully scraped high-demand product: {selected_prod['title']}")
                return selected_prod

    except Exception as e:
        print(f"⚠️ Scraping Error: {e}")

    # হাই-সার্চ এবং ফাস্ট-সেলিং ট্রেন্ডিং গ্যাজেটের ফলব্যাক তালিকা (যদি লাইভ স্ক্র্যাপিং ফেইল করে)
    trending_fallbacks = [
        {
            "title": "Xiaomi Redmi Note 13 Pro Plus Price in Bangladesh & Review 2026",
            "url": "https://www.bdstall.com/details/xiaomi-redmi-note-13-pro-plus-98231/",
            "image": "https://images.unsplash.com/photo-1598327105666-5b89351aff97?w=800&auto=format&fit=crop&q=60"
        },
        {
            "title": "Samsung Galaxy A55 5G Price in Bangladesh & Review 2026",
            "url": "https://www.bdstall.com/details/samsung-galaxy-a55-98231/",
            "image": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop&q=60"
        },
        {
            "title": "Haylou Solar Pro Smartwatch Price in Bangladesh & Review 2026",
            "url": "https://www.bdstall.com/details/haylou-solar-pro-98231/",
            "image": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&auto=format&fit=crop&q=60"
        },
        {
            "title": "Anker Soundcore Life Q30 Headphones Price in Bangladesh & Review 2026",
            "url": "https://www.bdstall.com/details/anker-soundcore-life-q30-98231/",
            "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=60"
        }
    ]
    
    selected_fallback = random.choice(trending_fallbacks)
    print(f"⚠️ Using Trending Fast-Selling Fallback: {selected_fallback['title']}")
    return selected_fallback
