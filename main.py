import os
import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON")

AFFILIATE_TAG = "?ref=379372"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

def get_blogger_service():
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

def fetch_bdstall_product():
    url = "https://www.bdstall.com/technology/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # BDStall HTML selector
    product = soup.find('div', class_='product-spec')
    if not product:
        product = soup.find('div', class_='product-list') or soup.find('div', class_='prod-box')
        
    if not product:
        raise Exception("BDStall থেকে কোনো প্রোডাক্ট স্ক্র্যাপ করা যায়নি। HTML স্ট্রাকচার পরিবর্তন হতে পারে।")
        
    title = product.find('h2').text.strip()
    raw_link = "https://www.bdstall.com" + product.find('a')['href']
    image_url = product.find('img')['src']
    
    affiliate_link = raw_link + AFFILIATE_TAG
    return title, image_url, affiliate_link

def generate_review(title):
    prompt = f"""
    একটি টেক ব্লগের জন্য আকর্ষনীয় বাংলা রিভিউ পোস্ট লিখুন:
    প্রোডাক্টের নাম: {title}
    
    গঠন:
    ১. প্রারম্ভিক কথা
    ২. প্রধান ফিচারসমূহ (বুলেট পয়েন্টে)
    ৩. কেন কেনা উচিত
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    print("🚀 Blogger Auto-Post Bot Started...")
    
    # ১. স্ক্র্যাপিং
    title, image_url, affiliate_link = fetch_bdstall_product()
    print(f"📦 Product Found: {title}")
    
    # ২. রিভিউ তৈরি
    review_text = generate_review(title)
    review_html = review_text.replace('\n', '<br>')
    
    formatted_content = f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px;" />
    </div>
    <div>
        {review_html}
    </div>
    <br>
    <div style="text-align: center; margin-top: 20px;">
        <a href="{affiliate_link}" target="_blank" style="background-color: #0866ff; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">🛒 বিস্তারিত জানুন বা অর্ডার করুন</a>
    </div>
    """
    
    # ৩. ব্লগারে পাবলিশ
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
