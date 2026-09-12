import os
import json
import random
import requests
from bs4 import BeautifulSoup
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON")

AFFILIATE_TAG = "?ref=379372"

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def get_blogger_service():
    """Blogger API কানেক্ট করার ফাংশন"""
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

def fetch_bdstall_product():
    """BDStall থেকে গ্যাজেট, হাই-কোয়ালিটি ছবি ও লিঙ্ক এক্সট্র্যাক্ট করা"""
    target_urls = [
        "https://www.bdstall.com/technology/",
        "https://www.bdstall.com/air-conditioner/",
        "https://www.bdstall.com/laptop/",
        "https://www.bdstall.com/mobile-phone/",
        "https://www.bdstall.com/cc-camera/"
    ]
    url = random.choice(target_urls)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    ignore_keywords = ['bdstall', 'logo', 'banner', 'icon', 'categories', 'বাংলা', 'view all', 'details']

    for img in soup.find_all('img'):
        alt_text = img.get('alt', '').strip()
        if len(alt_text) > 12 and not any(ign in alt_text.lower() for ign in ignore_keywords):
            parent_a = img.find_parent('a', href=True)
            if parent_a:
                link = parent_a['href']
                src = img.get('data-src') or img.get('src') or img.get('data-original') or ""
                
                if src and ('product' in src or 'images' in src or 'upload' in src or '.jpg' in src or '.png' in src or '.webp' in src):
                    products.append({
                        'title': alt_text,
                        'link': link,
                        'img': src
                    })

    if not products:
        for a in soup.find_all('a', href=True):
            title = a.text.strip()
            if len(title) > 15 and not any(ign in title.lower() for ign in ignore_keywords):
                link = a['href']
                img = a.find('img')
                src = img.get('data-src') or img.get('src') if img else ""
                products.append({'title': title, 'link': link, 'img': src})

    if not products:
        raise Exception("BDStall থেকে কোনো প্রোডাক্ট পাওয়া যায়নি।")

    selected = random.choice(products)
    title = selected['title']
    raw_link = selected['link']
    image_url = selected['img']

    if not raw_link.startswith('http'):
        raw_link = "https://www.bdstall.com" + (raw_link if raw_link.startswith('/') else '/' + raw_link)

    if image_url and not image_url.startswith('http'):
        image_url = "https://www.bdstall.com" + (image_url if image_url.startswith('/') else '/' + image_url)

    affiliate_link = raw_link + AFFILIATE_TAG
    return title, image_url, affiliate_link

def generate_seo_review(title):
    """গুগল SEO ফ্রেন্ডলি কন্টেন্ট জেনারেট (স্টার/হ্যাশ মার্ক ছাড়া HTML ফরম্যাটে)"""
    prompt = f"""
    আপনি একজন পেশাদার SEO বাংলা টেক ব্লগ রাইটার। নিচের প্রোডাক্টটির জন্য একটি ১০০% SEO Optimized রিভিউ পোস্ট লিখুন।
    
    প্রোডাক্টের নাম: {title}
    
    গুরুত্বপূর্ণ নিয়ম ও ফরম্যাটিং নির্দেশনাবলী:
    ১. কোনো অবস্থাতেই কোনো স্টার (*) বা হ্যাশ (#) চিহ্ন ব্যবহার করবেন না। 
    ২. কোনো জায়গায় বোল্ড বা লিস্ট বোঝাতে সরাসরি HTML ট্যাগ ব্যবহার করুন। যেমন: <h2>, <h3>, <b>, <ul>, <li> ইত্যাদি।
    ৩. যেখানে বুলেট পয়েন্ট দেওয়ার দরকার সেখানে কেবল HTML <ul> এবং <li> ট্যাগ ব্যবহার করুন।
    ৪. পোস্টের শুরুতে ২ লাইনের চমৎকার ভূমিকা দিন।
    ৫. নিচের সেকশনগুলো HTML হেডারে সাজিয়ে লিখুন:
       - <h2>{title} এর বিস্তারিত ফিচার ও স্পেসিফিকেশন</h2> (bullet points হিসেবে <ul><li>...</li></ul> দিন)
       - <h2>কেন এই প্রোডাক্টটি কেনা উচিত?</h2>
       - <h2>বাংলাদেশে {title} এর দাম ও বাজারের অবস্থান</h2>
       - <h2>আমাদের চূড়ান্ত মতামত</h2>
    ৬. কন্টেন্টটি সার্চ ইঞ্জিনে র‍্যাঙ্ক করার উপযোগী বিস্তারিত তথ্যে সমৃদ্ধ করুন।
    """
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt
    )
    return response.text

def main():
    print("🚀 Blogger Auto-Post Bot Started...")
    
    # ১. স্ক্র্যাপিং
    title, image_url, affiliate_link = fetch_bdstall_product()
    print(f"📦 Product Found: {title}")
    print(f"🖼️ Image URL: {image_url}")
    print(f"🔗 Affiliate Link: {affiliate_link}")
    
    # ২. SEO রিভিউ জেনারেট
    review_html = generate_seo_review(title)
    
    # হাই-কোয়ালিটি ইমেজের জন্য HTML ট্যাগের স্ট্রাকচার
    img_tag = f"""
    <div style="text-align: center; margin: 20px 0;">
        <img src="{image_url}" alt="{title} Price in Bangladesh" style="max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); display: inline-block;" />
    </div>
    """ if image_url else ''
    
    # কল-টু-অ্যাকশন (CTA) বাটন
    cta_button = f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{affiliate_link}" target="_blank" rel="nofollow sponsored" style="background-color: #28a745; color: white; padding: 14px 28px; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">🛒 বর্তমান দাম জানুন এবং অর্ডার করুন</a>
    </div>
    """
    
    formatted_content = f"{img_tag}{review_html}<br>{cta_button}"
    
    # SEO ফ্রেন্ডলি পোস্ট টাইটেল (* বা # মুক্ত)
    post_title = f"{title} দাম বাংলাদেশে এবং বিস্তারিত রিভিউ ২০২৬"
    
    # ৩. ব্লগারে অটো-পোস্ট
    blogger_service = get_blogger_service()
    body = {
        "kind": "blogger#post",
        "title": post_title,
        "content": formatted_content,
        "labels": ["Tech Review", "BDStall", "Buying Guide"]
    }
    
    res = blogger_service.posts().insert(blogId=BLOG_ID, body=body, isDraft=False).execute()
    print(f"✅ Successfully Published to Blogger: {res.get('url')}")

if __name__ == "__main__":
    main()
