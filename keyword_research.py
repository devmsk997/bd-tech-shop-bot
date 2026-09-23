import random
import requests
from bs4 import BeautifulSoup

def get_high_search_product():
    """
    বিডি স্টলের (BDStall) বিভিন্ন টেক ক্যাটাগরি থেকে স্বয়ংক্রিয়ভাবে প্রোডাক্ট ও ইমেজ স্ক্র্যাপ করে।
    """
    target_urls = [
        "https://www.bdstall.com/mobile-phone/",
        "https://www.bdstall.com/gadgets/",
        "https://www.bdstall.com/smart-watch/",
        "https://www.bdstall.com/sound-system/",
        "https://www.bdstall.com/laptop-computer/",
        "https://www.bdstall.com/networking-router/",
        "https://www.bdstall.com/cc-camera/",
        "https://www.bdstall.com/gaming-accessories/",
        "https://www.bdstall.com/technology/",
        "https://www.bdstall.com/camera/",
        "https://www.bdstall.com/television/",
        "https://www.bdstall.com/desktop-computer/"
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
            
            # একাধিক সম্ভাব্য প্রোডাক্ট কন্টেইনার বা কার্ড খোঁজা (যাতে ফেইল না করে)
            product_cards = (
                soup.find_all('div', class_='ref_hot_deal_single') or 
                soup.find_all('div', class_='product-list') or
                soup.find_all('div', class_='col-sm-4') or
                soup.find_all('div', class_='item-grid')
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

                    # ইমেজের আসল সোর্স বা লেজি-লোড অ্যাট্রিবিউট চেক করা
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
                print(f"✅ Successfully scraped product: {selected_prod['title']}")
                return selected_prod

    except Exception as e:
        print(f"⚠️ Scraping Error: {e}")

    # ফুলপ্রুফ ব্যাকআপ প্রোডাক্ট (একটি জেনুইন ও রিয়েল সচল ইমেজ সহ)
    return {
        "title": "Apple iPhone 15 Pro Max Price in Bangladesh & Review 2026",
        "url": "https://www.bdstall.com/details/apple-iphone-15-pro-max-98231/",
        "image": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=800&auto=format&fit=crop&q=60"
    }
