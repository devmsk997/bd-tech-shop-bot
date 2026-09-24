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
    
    # একাধিক এপিআই ভার্সন এবং মডেলের কম্বিনেশন (যাতে কোনোভাবেই ফেইল না করে)
    combinations = [
        ("v1", "gemini-1.5-flash"),
        ("v1beta", "gemini-1.5-flash"),
        ("v1", "gemini-1.5-pro"),
        ("v1beta", "gemini-pro")
    ]

    for api_version, model_name in combinations:
        endpoint = f"https://generativelanguage.googleapis.com/{api_version}/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        
        for attempt in range(1, 3):
            try:
                print(f"🤖 Trying API [{api_version}] with Model: {model_name} (Attempt {attempt})...")
                response = requests.post(endpoint, json=payload, timeout=45)
                res_json = response.json()
                
                if response.status_code == 200:
                    if 'candidates' in res_json and res_json['candidates']:
                        text = res_json['candidates'][0]['content']['parts'][0]['text']
                        print(f"✅ Successfully generated content using {model_name} on {api_version}")
                        return text
                else:
                    err_msg = res_json.get('error', {}).get('message', 'Unknown Error')
                    print(f"⚠️ API Error ({response.status_code}) [{model_name}]: {err_msg}")
                    
                    # কোটা বা রেট লিমিট ইস্যু হলে একটু অপেক্ষা করা
                    if "rate limit" in err_msg.lower() or "quota" in err_msg.lower():
                        time.sleep(15)
                        
            except Exception as e:
                print(f"⚠️ Exception with {model_name}: {e}")
                time.sleep(5)

    raise Exception("❌ Gemini API failed across all available models and versions.")
