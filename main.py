import os
import json
import time
import requests
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_fixed

from keyword_research import get_high_search_product

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

AFFILIATE_TAG = "?ref=379372"

client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def get_caching_cdn_image_url(image_url):
    """
    BDStall hotlink block bypass system.
    Directly converts BDStall image URL into wsrv.nl CDN proxy URL.
    """
    if not image_url:
        return None
    
    clean_url = image_url.replace("https://", "").replace("http://", "")
    return f"https://wsrv.nl/?url={clean_url}&output=jpg"

def get_blogger_service():
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(10),
    reraise=True
)
def generate_seo_review(title):
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
    """
    
    # গুগলের নির্দেশিত সঠিক মডেল
    model_name = "gemini-3.6-flash"
    
    try:
        print(f"🤖 Requesting content generation using model: {model_name}")
        chat = client.chats.create(model=model_name)
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        err_msg = str(e)
        print(f"⚠️ API Request error for {model_name}: {err_msg}")
        raise e

def post_to_facebook(title, product_url):
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
    
    product_data = get_high_search_product()
    title = product_data['title']
    raw_url = product_data['url']
    raw_image_url = product_data['image']
    
    if raw_image_url:
        if raw_image_url.startswith('//'):
            raw_image_url = 'https:' + raw_image_url
        elif raw_image_url.startswith('http://'):
            raw_image_url = raw_image_url.replace('http://', 'https://')
        elif not raw_image_url.startswith('http'):
            raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')
            
    working_image_url = get_caching_cdn_image_url(raw_image_url)
    
    affiliate_link = raw_url + AFFILIATE_TAG if "?" not in raw_url else raw_url + "&ref=379372"
    
    print(f"📦 Product Found: {title}")
    print(f"🖼️ Working Image URL: {working_image_url}")
    print(f"🔗 Affiliate Link: {affiliate_link}")
    
    review_html = generate_seo_review(title)
    
    featured_img_tag = f"""
    <div class="separator" style="clear: both; text-align: center; margin-bottom: 25px;">
        <a href="{working_image_url}" style="margin-left: 1em; margin-right: 1em;">
            <img border="0" src="{working_image_url}" alt="{title}" title="{title}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);" />
        </a>
    </div>
    """ if working_image_url else ''
    
    cta_button = f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{affiliate_link}" target="_blank" rel="nofollow sponsored" style="background-color: #28a745; color: white; padding: 14px 28px; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">🛒 বর্তমান দাম জানুন এবং অর্ডার করুন</a>
    </div>
    """
    
    formatted_content = f"{featured_img_tag}{review_html}<br>{cta_button}"
    
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

    post_to_facebook(title, blog_post_url)

if __name__ == "__main__":
    main()
