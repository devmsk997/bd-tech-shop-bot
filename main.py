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

# GenAI Client Initialization
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
    """BDStall থেকে প্রোডাক্টের আসল নাম, লিংক ও ছবি স্ক্র্যাপ করার ফলব্যাক লজিক"""
    url = "https://www.bdstall.com/technology/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # BDStall-এর সকল প্রোডাক্ট লিংক খুঁজে বের করা
    all_links = soup.find_all('a', href=True)
    
    selected_title = ""
    selected_link = ""
    selected_img = ""

    for a in all_links:
        href = a['href']
        # যেসব লিংকে প্রোডাক্ট আইডি বা টেকনোলজি ক্যাটালগ রয়েছে
        if ('/details/' in href or '/product/' in href or '.html' in href) and len(a.text.strip()) > 10:
            text = a.text.strip()
            if text.lower() not in ["details", "more info", "বাংলা", "view details"]:
                selected_title = text
                selected_link = href
                
                # যদি ইমেজের ট্যাগ থাকে
                img = a.find('img') or a.parent.find('img')
                if img:
                    selected_img = img.get('data-src') or img.get('src') or ""
                break
                
    if not selected_title:
        # ফলব্যাক: যেকোনো হেইডিং বা প্রোডাক্ট টাইটেল খোঁজা
        headers_tags = soup.find_all(['h2', 'h3'])
        for h in headers_tags:
            if len(h.text.strip()) > 10:
                selected_title = h.text.strip()
                parent_a = h.find_parent('a') or h.find('a')
                if parent_a and parent_a.get('href'):
                    selected_link = parent_a['href']
                break

    if not selected_title:
        raise Exception("BDStall পেজ থেকে কোনো প্রোডাক্ট তথ্য ফিল্টার করা সম্ভব হয়নি।")

    # লিংক ফরম্যাটিং
    if not selected_link.startswith('http'):
        selected_link = "https://www.bdstall.com" + (selected_link if selected_link.startswith('/') else '/' + selected_link)

    # ইমেজ লিংক ফরম্যাটিং
    if selected_img and not selected_img.startswith('http'):
        selected_img = "https://www.bdstall.com" + (selected_img if selected_img.startswith('/') else '/' + selected_img)

    affiliate_link = selected_link + AFFILIATE_TAG
    return selected_title, selected_img, affiliate_link

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
    
    # ২. রিভিউ জেনারেট
    review_text = generate_review(title)
    review_html = review_text.replace('\n', '<br>')
    
    # HTML ফরম্যাটিং
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
