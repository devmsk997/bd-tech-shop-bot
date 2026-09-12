import os
import json
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

# GenAI Client
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
    """BDStall থেকে প্রোডাক্টের আসল নাম, লিংক ও ছবি স্ক্র্যাপ করার নির্ভুল ফাংশন"""
    url = "https://www.bdstall.com/technology/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # BDStall-এর প্রোডাক্ট কন্টেইনারগুলো খুঁজে বের করা
    products = soup.find_all('div', class_='product-spec') or soup.find_all('div', class_='p_box') or soup.find_all('div', class_='ref-product')
    
    selected_product = None
    for p in products:
        title_tag = p.find('h2') or p.find('h3') or p.find('a')
        if title_tag and len(title_tag.text.strip()) > 5 and title_tag.text.strip() != "বাংলা":
            selected_product = p
            break
            
    if not selected_product:
        raise Exception("BDStall থেকে সঠিক কোনো প্রোডাক্ট স্ক্র্যাপ করা সম্ভব হয়নি।")

    # প্রোডাক্টের টাইটেল সংগ্রহ
    title_element = selected_product.find('h2') or selected_product.find('h3') or selected_product.find('a')
    title = title_element.text.strip()
    
    # লিংক সংগ্রহ
    link_element = selected_product.find('a', href=True)
    raw_link = link_element['href']
    if not raw_link.startswith('http'):
        raw_link = "https://www.bdstall.com" + (raw_link if raw_link.startswith('/') else '/' + raw_link)
        
    # ইমেজ URL সঠিক ফরম্যাটে এক্সট্র্যাক্ট করা
    img_element = selected_product.find('img')
    image_url = ""
    if img_element:
        # data-src বা src থেকে আসল ছবির লিংক নেওয়া
        image_url = img_element.get('data-src') or img_element.get('src') or ""
        
    if image_url and not image_url.startswith('http'):
        image_url = "https://www.bdstall.com" + (image_url if image_url.startswith('/') else '/' + image_url)

    affiliate_link = raw_link + AFFILIATE_TAG
    return title, image_url, affiliate_link

def generate_review(title):
    """Gemini AI (gemini-3.6-flash) দিয়ে রিভিউ জেনারেট"""
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
    
    # ২. রিভিউ জেনারেট
    review_text = generate_review(title)
    review_html = review_text.replace('\n', '<br>')
    
    # HTML ফরম্যাটিং (ছবি নিশ্চিত করার ট্যাগসহ)
    img_tag = f'<img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px;" />' if image_url else ''
    
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
