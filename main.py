import os
import json
import time
import urllib.parse
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from keyword_research import get_high_search_product

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON")
FB_PAGE_ID = os.environ.get("FB_PAGE_ID")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN")

AFFILIATE_TAG = "?ref=379372"

def get_blogger_service():
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

def generate_seo_review(title):
    prompt = f"""
    আপনি একজন SEO বাংলা টেক ব্লগ রাইটার। নিচের প্রোডাক্টটির জন্য সংক্ষিপ্ত ও আকর্ষণীয় রিভিউ পোস্ট লিখুন।
    প্রোডাক্ট: {title}
    
    নিয়মাবলী:
    ১. কোনো স্টার (*) বা হ্যাশ (#) ব্যবহার করবেন না।
    ২. ফরম্যাটিংয়ের জন্য কেবল HTML ট্যাগ (<h2>, <h3>, <b>, <ul>, <li>) ব্যবহার করুন।
    ৩. সেকশনসমূহ:
       - <h2>{title} এর স্পেসিফিকেশন</h2>
       - <h2>কেন এই প্রোডাক্টটি কেনা উচিত?</h2>
       - <h2>বাংলাদেশে {title} এর দাম</h2>
       - <h2>আমাদের মতামত</h2>
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    model_name = "gemini-3.6-flash"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"

    for attempt in range(1, 4):
        try:
            print(f"🤖 Requesting API using model: {model_name} (Attempt {attempt})...")
            response = requests.post(endpoint, json=payload, timeout=30)
            res_json = response.json()
            
            if response.status_code == 200:
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                return text
            else:
                err_msg = res_json.get('error', {}).get('message', 'Unknown Error')
                print(f"⚠️ API Error ({response.status_code}): {err_msg}")
                if response.status_code in [503, 429]:
                    print("⏳ Server busy or rate limited. Retrying in 10 seconds...")
                    time.sleep(10)
                else:
                    break
        except requests.exceptions.Timeout:
            print("⏳ Request timed out. Retrying...")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ Exception: {e}")
            time.sleep(3)

    raise Exception("❌ Gemini API failed to return response.")

def post_to_facebook(title, product_url):
    """Facebook Page Auto Post System"""
    if not FB_PAGE_ID or not FB_ACCESS_TOKEN:
        print("⚠️ Facebook Credentials missing in GitHub Secrets. Skipping FB Post.")
        return

    url = f"https://graph.facebook.com/v18.0/{FB_PAGE_ID}/feed"
    
    message = (
        f"🔥 New Tech Product Review!\n\n"
        f"📌 {title}\n\n"
        f"👉 আমাদের ব্লগে বিস্তারিত রিভিউ এবং অরিজিনাল দাম দেখে নিন:\n{product_url}\n\n"
        f"👤 Post Managed By: Md Solayman\n"
        f"🔗 Profile: https://www.facebook.com/MdSolayman996/"
    )
    
    payload = {
        'message': message,
        'link': product_url,
        'access_token': FB_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload, timeout=12)
        res_data = response.json()
        if response.status_code == 200 and 'id' in res_data:
            print(f"✅ Successfully posted to Facebook Page! Post ID: {res_data['id']}")
        else:
            print(f"❌ Facebook Post Failed: {res_data}")
    except Exception as e:
        print(f"⚠️ Error posting to Facebook: {e}")

def main():
    print("🚀 Blogger Auto-Post Bot Started...")
    
    product_data = get_high_search_product()
    title = product_data['title']
    raw_url = product_data['url']
    raw_image_url = product_data['image']
    
    # ইমেজ লিঙ্ক প্রসেসিং (Direct Image CDN Fix)
    if raw_image_url:
        if raw_image_url.startswith('//'):
            raw_image_url = 'https:' + raw_image_url
        elif raw_image_url.startswith('http://'):
            raw_image_url = raw_image_url.replace('http://', 'https://')
        elif not raw_image_url.startswith('http'):
            raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')
            
        # Blogger Hotlink Bypass Image Service
        working_image_url = f"https://images.weserv.nl/?url={urllib.parse.quote(raw_image_url)}&w=600&output=jpg"
    else:
        working_image_url = ""
    
    affiliate_link = raw_url + AFFILIATE_TAG if "?" not in raw_url else raw_url + "&ref=379372"
    
    print(f"📦 Product Found: {title}")
    print(f"🖼️ Working Image URL: {working_image_url}")
    print(f"🔗 Affiliate Link: {affiliate_link}")
    
    review_html = generate_seo_review(title)
    
    featured_img_tag = f"""
    <div class="separator" style="clear: both; text-align: center; margin-bottom: 25px;">
        <a href="{affiliate_link}" target="_blank" rel="nofollow sponsored">
            <img border="0" src="{working_image_url}" alt="{title}" title="{title}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);" />
        </a>
    </div>
    """ if working_image_url else ''
    
    cta_button = f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{affiliate_link}" target="_blank" rel="nofollow sponsored" style="background-color: #28a745; color: white; padding: 14px 28px; text-decoration: none; font-size: 18px; font-weight: bold; border-radius: 8px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">🛒 বর্তমান দাম জানুন এবং অর্ডার করুন</a>
    </div>
    """
    
    formatted_content = f"{featured_img_tag}\n{review_html}\n<br>\n{cta_button}"
    
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

    # ফেসবুক পেজে অটো-পোস্ট
    post_to_facebook(title, blog_post_url)

if __name__ == "__main__":
    main()
