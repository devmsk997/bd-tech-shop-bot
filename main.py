import os
import json
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON")

# অ্যাফিলিয়েট আইডি
AFFILIATE_TAG = "?ref=379372"

# Gemini Config
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

def get_blogger_service():
    """Blogger API কানেক্ট করার ফাংশন"""
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

def fetch_bdstall_product():
    """BDStall থেকে প্রোডাক্টের নাম, ফিচারড ইমেজ ও লিংক সংগ্রহ করে"""
    url = "https://www.bdstall.com/technology/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    product = soup.find('div', class_='product-spec') 
    title = product.find('h2').text.strip()
    raw_link = "https://www.bdstall.com" + product.find('a')['href']
    image_url = product.find('img')['src']
    
    affiliate_link = raw_link + AFFILIATE_TAG
    return title, image_url, affiliate_link

def generate_review(title):
    """Gemini AI দিয়ে বাংলা কন্টেন্ট তৈরি"""
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
    print("🚀 BDStall Blogger Auto-Post Bot Started...")
    try:
        title, image_url, affiliate_link = fetch_bdstall_product()
        review_text = generate_review(title)
        
        # ব্লগের জন্য ফিচারড ইমেজ ও অ্যাফিলিয়েট বাটনসহ HTML সাজানো
        formatted_content = f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="{image_url}" alt="{title}" style="max-width: 100%; height: auto; border-radius: 8px;" />
        </div>
        <div>
            {review_text.replace('\n', '<br>')}
        </div>
        <br>
        <div style="text-align: center; margin-top: 20px;">
            <a href="{affiliate_link}" target="_blank" style="background-color: #0866ff; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px; display: inline-block;">🛒 বিস্তারিত জানুন বা অর্ডার করুন</a>
        </div>
        """
        
        # ব্লগারে পোস্ট পাঠানো
        blogger_service = get_blogger_service()
        body = {
            "kind": "blogger#post",
            "title": title,
            "content": formatted_content,
            "labels": ["Tech Review", "BDStall"]
        }
        
        res = blogger_service.posts().insert(blogId=BLOG_ID, body=body, isDraft=False).execute()
        print(f"✅ Successfully Published to Blogger: {res.get('url')}")
        
    except Exception as e:
        print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    main()
