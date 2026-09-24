import random
import requests
from bs4 import BeautifulSoup

def get_high_search_product():
    """
    সরাসরি বিডিষ্টল (BDStall) থেকে লাইভ হাই-সার্চ এবং ট্রেন্ডিং টেক প্রোডাক্ট ও তাদের আসল ছবি স্ক্র্যাপ করে।
    """
    target_urls = [
        "https://www.bdstall.com/mobile-phone/",
        "https://www.bdstall.com/smart-watch/",
        "https://www.bdstall.com/gadgets/",
        "https://www.bdstall.com/laptop/",
        "https://www.bdstall.com/headphone/"
    ]
    
    # র‍্যান্ডমলি একটি ক্যাটাগরি পেজ সিলেক্ট করা যাতে প্রতিবার ভিন্ন ক্যাটাগরি থেকে প্রোডাক্ট আসে
    selected_url = random.choice(target_urls)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.bdstall.com/"
    }

    try:
        response = requests.get(selected_url, headers=headers, timeout=20)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # বিডিষ্টলের পেজ থেকে প্রোডাক্ট কার্ডগুলো খুঁজে বের করা
            product_cards = (
                soup.find_all('div', class_='ref_hot_deal_single') or 
                soup.find_all('div', class_='product-list') or
                soup.find_all('div', class_='col-sm-4') or
                soup.find_all('div', class_='item-grid') or
                soup.find_all('div', class_='product-item') or
                soup.find_all('div', class_='box') or
                soup.find_all('div', class_='col-md-4')
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

                    # বিডিষ্টলের আসল প্রোডাক্ট ইমেজ লিংক সংগ্রহ করা
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
                # ডুপ্লিকেট এড়াতে র‍্যান্ডমলি একটি লাইভ প্রোডাক্ট সিলেক্ট করা
                selected_prod = random.choice(scraped_products)
                print(f"✅ সফলভাবে বিডিষ্টল থেকে লাইভ প্রোডাক্ট ও আসল ছবি পাওয়া গেছে: {selected_prod['title']}")
                return selected_prod

    except Exception as e:
        print(f"⚠️ লাইভ স্ক্র্যাপিং এরর: {e}")

    print("⚠️ লাইভ স্ক্র্যাপিং থেকে প্রোডাক্ট পাওয়া যায়নি।")
    return None
