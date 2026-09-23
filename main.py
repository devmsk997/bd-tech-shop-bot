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

AFFILIATE_TAG = "?ref=379372"

def get_caching_cdn_image_url(image_url):
    if not image_url:
        return None
    encoded_url = urllib.parse.quote(image_url, safe='')
    return f"https://wsrv.nl/?url={encoded_url}&output=jpg&n=-1"

def get_blogger_service():
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

def generate_seo_review(title):
    prompt = f"""
    আপনি একজন SEO বাংলা টেক ব্লগ রাইটার। নিচের প্রোডাক্টটির জন্য একটি সংক্ষিপ্ত ও আকর্ষণীয় রিভিউ পোস্ট লিখুন।
    প্রোডাক্টের নাম: {title}
    
    গুরুত্বপূর্ণ নিয়মাবলী:
    ১. কোনো অবস্থাতেই স্টার (*) বা হ্যাশ (#) চিহ্ন ব্যবহার করবেন না।
    ২. ফরম্যাটিংয়ের জন্য কেবল HTML ট্যাগ (<h2>, <h3>, <b>, <ul>, <li>) ব্যবহার করুন।
    ৩. নিচের সেকশনগুলো সাজিয়ে লিখুন:
       - <h2>{title} এর বিস্তারিত স্পেসিফিকেশন</h2>
       - <h2>কেন এই প্রোডাক্টটি কেনা উচিত?</h2>
       - <h2>বাংলাদেশে {title} এর দাম ও বাজারের অবস্থা</h2>
       - <h2>আমাদের চূড়ান্ত মতামত</h2>
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    # আফিশিয়াল স্থিতিশীল মডেল নেম
    model_name = "gemini-1.5-flash"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"

    # এপিআই লিমিটের জন্য ৫ বার রিট্রাই লুপ
    for attempt in range(1, 6):
        try:
            print(f"🤖 Requesting API using model: {model_name} (Attempt {attempt})...")
            response = requests.post(endpoint, json=payload, timeout=60)
            res_json = response.json()
            
            if response.status_code == 200:
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                return text
            else:
                err_msg = res_json.get('error', {}).get('message', 'Unknown Error')
                print(f"⚠️ API Error ({response.status_code}): {err_msg}")
                # ৪২৯ এরর আসলে একটু বেশি সময় (২৫ সেকেন্ড) বিরতি দেওয়া হবে
                if response.status_code in [503, 429]:
                    print("⏳ Rate limited. Retrying in 25 seconds...")
                    time.sleep(25)
                else:
                    break
        except requests.exceptions.Timeout:
            print("⏳ Request timed out. Retrying in 10 seconds...")
            time.sleep(10)
        except Exception as e:
            print(f"⚠️ Exception: {e}")
            time.sleep(5)

    raise Exception("❌ Gemini API failed to return response after retries.")

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

if __name__ == "__main__":
    main()
