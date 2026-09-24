import random
import requests
from bs4 import BeautifulSoup

def get_high_search_product():
    """
    বিডিষ্টল (BDStall) থেকে লাইভ হাই-সার্চ এবং ট্রেন্ডিং টেক প্রোডাক্ট ও তাদের আসল ছবি স্ক্র্যাপ করার উন্নত মেথড।
    """
    target_urls = [
        "https://www.bdstall.com/mobile-phone/",
        "https://www.bdstall.com/smart-watch/",
        "https://www.bdstall.com/gadgets/",
        "https://www.bdstall.com/laptop/",
        "https://www.bdstall.com/headphone/"
    ]
    
    selected_url = random.choice(target_urls)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Referer": "https://www.bdstall.com/",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        response = requests.get(selected_url, headers=headers, timeout=20)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            scraped_products = []
            
            # পদ্ধতি ১: যেকোনো প্রোডাক্ট ট্যাগ বা লিংক খোঁজা যার ভেতরে ছবি ও টেক্সট আছে
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                # বিডিষ্টলের প্রডাক্ট ডিটেইলস পেজের লিংক প্যাটার্ন চেক করা
                if '/details/' in href:
                    img_tag = a_tag.find('img') or a_tag.find_parent().find('img')
                    if img_tag:
                        title = img_tag.get('alt', '').strip() or a_tag.text.strip()
                        if not title or len(title) < 5:
                            # যদি অ্যাংকরের ভেতর টাইটেল না থাকে, আশেপাশে খোঁজা
                            parent_div = a_tag.find_parent(['div', 'article', 'li'])
                            if parent_div:
                                title_tag = parent_div.find(['h2', 'h3', 'h4', 'span'], class_=['title', 'product-title', 'name']) or parent_div.find('a')
                                if title_tag:
                                    title = title_tag.text.strip()

                        if title and len(title) > 5:
                            product_url = href
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

            # যদি সরাসরি লিস্ট থেকে পাওয়া না যায়, তবে জেনেরিক কার্ড খুঁজবে
            if not scraped_products:
                cards = soup.find_all(['div', 'li'], class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower() or 'deal' in x.lower()))
                for card in cards:
                    a_tag = card.find('a', href=True)
                    img_tag = card.find('img')
                    if a_tag and img_tag:
                        title = img_tag.get('alt', '').strip() or a_tag.text.strip()
                        href = a_tag['href']
                        if title and len(title) > 5 and '/details/' in href:
                            if not href.startswith('http'):
                                href = "https://www.bdstall.com" + href
                            img_src = img_tag.get('data-src') or img_tag.get('src', '')
                            if img_src:
                                if img_src.startswith('//'):
                                    img_src = 'https:' + img_src
                                elif not img_src.startswith('http'):
                                    img_src = "https://www.bdstall.com" + img_src

                                scraped_products.append({
                                    "title": f"{title} Price in Bangladesh & Review 2026",
                                    "url": href,
                                    "image": img_src
                                })

            # ইউনিক ও ডুপ্লিকেট ফিল্টার করার পর একটি প্রোডাক্ট সিলেক্ট করা
            if scraped_products:
                # ডুপ্লিকেট ডিকশনারি রিমুভ করার জন্য ইউআরএল দিয়ে ইউনিক লিস্ট তৈরি
                unique_dict = {p['url']: p for p in scraped_products}
                unique_list = list(unique_dict.values())
                
                selected_prod = random.choice(unique_list)
                print(f"✅ সফলভাবে বিডিষ্টল থেকে লাইভ প্রোডাক্ট ও আসল ছবি পাওয়া গেছে: {selected_prod['title']}")
                return selected_prod

    except Exception as e:
        print(f"⚠️ লাইভ স্ক্র্যাপিং এরর: {e}")

    print("⚠️ লাইভ স্ক্র্যাপিং থেকে প্রোডাক্ট পাওয়া যায়নি।")
    return None
