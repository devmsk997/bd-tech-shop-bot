import os
import json
import random
import time
import requests
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_exponential

# keyword_research.py ফাইল থেকে স্ক্র্যাপ করার ফাংশন ইমপোর্ট
from keyword_research import get_high_search_product

# Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

AFFILIATE_TAG = "?ref=379372"

# Google GenAI Client Initialize
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def get_blogger_service():
    """Blogger API কানেক্ট করার ফাংশন"""
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=5, max=20),
    reraise=True
)
def generate_seo_review(title):
    """গুগল SEO ফ্রেন্ডলি কন্টেন্ট জেনারেট (HTML ফরম্যাটে)"""
    prompt = f"""
    আপনি একজন পেশাদার SEO বাংলা টেক ব্লগ রাইটার। নিচের প্রোডাক্টটির জন্য একটি ১০০% SEO Optimized রিভিউ পোস্ট লিখুন।
    
    প্রোডাক্টের নাম: {title}
    
    গুরুত্বপূর্ণ নিয়ম ও ফরম্যাটিং নির্দেশনাবলী:
    ১. কোনো অবস্থাতেই কোনো স্টার (*) বা হ্যাশ (#) চিহ্ন ব্যবহার করবেন না। 
    ২. কোনো জায়গায় বোল্ড বা লিস্ট বোঝাতে সরাসরি HTML ট্যাগ ব্যবহার করুন। যেমন: <h2>, <h3>, <b>, <ul>, <li> ইত্যাদি।
    ৩. যেখানে বুলেট পয়েন্ট দেওয়ার দরকার সেখানে কেবল HTML <ul> এবং <li> ট্যাগ ব্যবহার করুন।
    ৪. পোস্টের শুরুতে ২ লাইনের চমৎকার ভূমিকা দিন।
    ৫. নিচের সেকশনগুলো HTML হেডারে সাজিয়ে লিখুন:
       - <h2>{title} এর বিস্তারিত ফিচার ও স্পেসিফিকেশন</h2> (bullet points হিসেবে <ul><li>...</li></ul> দিন)
       - <h2>কেন এই প্রোডাক্টটি কেনা উচিত?</h2>
       - <h2>বাংলাদেশে {title} এর দাম ও বাজারের অবস্থান</h2>
       - <h2>আমাদের চূড়ান্ত মতামত</h2>
    ৬. কন্টেন্টটি সার্চ ইঞ্জিনে র‍্যাঙ্ক করার উপযোগী বিস্তারিত তথ্যে সমৃদ্ধ করুন।
    """
    
    models_to_try = ["gemini-3.6-flash"]
    
    for model_name in models_to_try:
        try:
            chat = client.chats.create(model=model_name)
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            print(f"⚠️ Model {model_name} failed ({e}). Switching to next model...")
            continue
            
    raise Exception("All Gemini models failed to process the request.")

def post_to_facebook(title, product_url):
    """ফেসবুক পেজে স্বয়ংক্রিয়ভাবে রিভিউ শেয়ার করার ফাংশন"""
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("⚠️ Facebook Credentials missing in GitHub Secrets. Skipping FB Post.")
        return

    url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"
    
    message = f"🔥 New Tech Product Review!\n\n📌 {title}\n\n👉 আমাদের ব্লগে বিস্তারিত রিভিউ এবং অরিজিনাল দাম দেখে নিন:\n{product_url}\n\n👤 Post Managed By: Md Solayman\n🔗 Profile: https://www.facebook.com/MdSolayman996/"
    
    payload = {
        'message': message,
        'link': product_url,
        'access_token': FB_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("✅ Successfully posted to Facebook Page!")
        else:
            print(f"❌ Facebook Post Failed: {response.text}")
    except Exception as e:
        print(f"⚠️ Error posting to Facebook: {e}")

def main():
    print("🚀 Blogger Auto-Post Bot Started...")
    
    # ১. keyword_research.py থেকে স্ক্র্যাপিং
    product_data = get_high_search_product()
    title = product_data['title']
    raw_url = product_data['url']
    image_url = product_data['image']
    
    # ইমেজের ইউআরএল প্রোপারলি ফিক্স করা
    if image_url:
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        elif not image_url.startswith('http'):
            image_url = 'https://www.bdstall.com/' + image_url.lstrip('/')
    
    affiliate_link = raw_url + AFFILIATE_TAG if "?" not in raw_url else raw_url + "&ref=379372"
    
    print(f"📦 Product Found: {title}")
    print(f"🖼️ Image URL: {image_url}")
    print(f"🔗 Affiliate Link: {affiliate_link}")
    
    # ২. SEO রিভিউ জেনারেট
    review_html = generate_seo_review(title)
    
    # ছবির HTML ট্যাগ (ব্লগার যেন ফার্স্ট ইমেজকে ফিচার্ড হিসেবে চিহ্নিত করতে পারে)
    featured_img_tag = f"""
    <div class="separator" style="clear: both; text-align: center; margin-bottom: 25px;">
        <a href="{image_url}" imageanchor="1" style="margin-left: 1em; margin-right: 1em;">
            <img border="0" data-original-height="800" data-original-width="800" src="{image_url}" alt="{title}" title="{title}" style="max-width: 100%; height: auto; border-radius: 8px;" />
        </a>
    </div>
    """ if image_url else ''
    
    # Call to Action Button
    cta_button = f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{affiliate_link}" target="_blank" rel="nofollow sponsored" style="background-color: #28a745; color: white; padding: 14px 28px; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">🛒 বর্তমান দাম জানুন এবং অর্ডার করুন</a>
    </div>
    """
    
    formatted_content = f"{featured_img_tag}{review_html}<br>{cta_button}"
    
    # ৩. ব্লগারে অটো-পোস্ট
    blogger_service = get_blogger_service()
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": formatted_content,
        "labels": ["Tech Review", "BDStall", "Buying Guide"]
    }
    
    res = blogger_service.posts().insert(blogId=BLOG_ID, body=body, isDraft=False).execute()
    blog_post_url = res.get('url')
    print(f"✅ Successfully Published to Blogger: {blog_post_url}")

    # ৪. ফেসবুকে অটো-পোস্ট
    post_to_facebook(title, blog_post_url)

if __name__ == "__main__":
    main()
