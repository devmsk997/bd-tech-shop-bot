import os
import time
import requests
import re

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def generate_seo_review(title):
    prompt = f"""
    আপনি একজন SEO বাংলা টেক ব্লগ রাইটার। নিচের প্রোডাক্টটির জন্য একটি সংক্ষিপ্ত ও আকর্ষণীয় রিভিউ পোস্ট লিখুন।
    প্রডাক্টের নাম: {title}
    
    গুরুত্বপূর্ণ নিয়মাবলী:
    ১. কোনো অবস্থাতেই স্টার (*) বা হ্যাশ (#) চিহ্ন ব্যবহার করবেন না।
    ২. ফরম্যাটিংয়ের জন্য কেবল HTML ট্যাগ (<h2>, <h3>, <b>, <ul>, <li>) ব্যবহার করুন।
    ৩. নিচের সেকশনগুলো সাজিয়ে লিখুন:
        - <h2>{title} এর বিস্তারিত স্পেসিফিকেশন</h2>
        - <h2>কেন এই প্রোডাক্টটি কেনা উচিত?</h2>
        - <h2>বাংলাদেশে {title} এর দাম ও বাজারের অবস্থা</h2>
        - <h2>আমাদের চূড়ান্ত মতামত</h2>
    """
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    # জেমিনির নিশ্চিত ও স্থিতিশীল লাইটওয়েট ফাস্ট মডেল
    model_name = "gemini-1.5-flash"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"

    for attempt in range(1, 6):
        try:
            print(f"🤖 Requesting API using model: {model_name} (Attempt {attempt})...")
            response = requests.post(endpoint, json=payload, timeout=60)
            res_json = response.json()
            
            if response.status_code == 200:
                if 'candidates' in res_json and res_json['candidates']:
                    text = res_json['candidates'][0]['content']['parts'][0]['text']
                    return text
                else:
                    print(f"⚠️ Warning: Response format unexpected: {res_json}")
            else:
                err_msg = res_json.get('error', {}).get('message', 'Unknown Error')
                print(f"⚠️ API Error ({response.status_code}): {err_msg}")
                
                # গুগল যত সেকেন্ড থামতে বলবে ঠিক তত সেকেন্ড ওয়েট করবে
                retry_match = re.search(r"Please retry in (\d+\.?\d*)s", err_msg)
                if retry_match:
                    wait_seconds = float(retry_match.group(1)) + 3
                else:
                    wait_seconds = 20.0
                
                print(f"⏳ Waiting for {wait_seconds:.1f} seconds...")
                time.sleep(wait_seconds)

        except Exception as e:
            print(f"⚠️ Exception: {e}. Waiting 10 seconds...")
            time.sleep(10)

    raise Exception("❌ Gemini API failed after retries.")
