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
    """BDStall থেকে গ্যাজেট, ছবি ও লিংক এক্সট্র্যাক্ট করার সহজ ও নির্ভরযোগ্য ফাংশন"""
    url = "https://www.bdstall.com/technology/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    products = []
    
    # BDStall পেজের সকল ইমেজ ট্যাগ বিশ্লেষণ করে প্রোডাক্ট খোঁজা
    for img in soup.find_all('img'):
        alt_text = img.get('alt', '').strip()
        # প্রোডাক্ট ইমেজের alt টেক্সট সাধারণত প্রোডাক্টের নাম হয়
        if len(alt_text) > 12 and not any(ign in alt_text.lower() for ign in ['bdstall', 'logo', 'banner', 'icon', 'categories', 'বাংলা']):
            parent_a = img.find_parent('a', href=True)
            if parent_a:
                link = parent_a['href']
                src = img.get('data-src') or img.get('src') or img.get('data-original') or ""
                
                products.append({
                    'title': alt_text,
                    'link': link,
                    'img': src
                })

    # যদি img-এর মাধ্যমে না পাওয়া যায়, তবে সরাসরি a ট্যাগ দিয়ে খুঁজবে
    if not products:
        for a in soup.find_all('a', href=True):
            title = a.text.strip()
            if len(title) > 15 and not any(ign in title.lower() for ign in ['bdstall', 'popular', 'technology', 'বাংলা', 'view all', 'details', 'privacy', 'about']):
                link = a['href']
                img = a.find('img')
                src = img.get('src') if img else ""
                products.append({
                    'title': title,
                    'link': link,
                    'img': src
                })

    if not products:
        raise Exception("BDStall থেকে কোনো প্রোডাক্ট স্ক্র্যাপ করা যায়নি।")

    # র‍্যান্ডম একটি রিয়েল প্রোডাক্ট নির্বাচন
    selected = random.choice(products)
    
    title = selected['title']
    raw_link = selected['link']
    image_url = selected['img']

    # URL ফরম্যাটিং
    if not raw_link.startswith('http'):
        raw_link = "https://www.bdstall.com" + (raw_link if raw_link.startswith('/') else '/' + raw_link)

    if image_url and not image_url.startswith('http'):
        image_url = "https://www.bdstall.com" + (image_url if image_url.startswith('/') else '/' + image_url)

    affiliate_link = raw_link + AFFILIATE_TAG
    return title, image_url, affiliate_link

def generate_review(title):
    """Gemini AI (gemini-3.6-flash) দিয়ে রিভিউ তৈরি"""
    prompt = f"""
    একটি টেক ব্লগের জন্য আকর্ষনীয় বাংলা রিভিউ পোস্ট লিখুন:
    প্রোডাক্টের নাম: {title}
    
    গঠন:
    ১. প্রারম্ভিক কথা
    ২. প্রধান ফিচারসমূহ (বুলেট পয়েন্টে)
    ৩. কেন কেনা উচিত
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
    
    # ২. রিভিউ জেনারেট
    review_text = generate_review(title)
    review_html = review_text.replace('\n', '<br>')
    
    # HTML ফরম্যাটিং
    img_tag = f'<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px; display: block; margin: 0 auto;" />' if image_url else ''
    
    formatted_content = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        {img_tag}
    </div>
    <div>
        {review_html}
    </div>
    <br>
    <div style="text-align: center; margin-top: 20px;">
        <a href="{affiliate_link}" target="_blank" style="background-color: #0866ff; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">🛒 বিস্তারিত জানুন বা অর্ডার করুন</a>
    </div>
    """
    
    # ৩. ব্লগারে অটো-পোস্ট
    blogger_service = get_blogger_service()
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": formatted_content,
        "labels": ["Tech Review", "BDStall"]
    }
    
    res = blogger_service.posts().insert(blogId=BLOG_ID, body=body, isDraft=False).execute()
    print(f"✅ Successfully Published to Blogger: {res.get('url')}")

if __name__ == "__main__":
    main()
