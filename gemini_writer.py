import os
import time
import requests

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
    
    # বর্তমান সময়ের সচল মডেলগুলোর তালিকা
    models_to_try = ["gemini-3.6-flash", "gemini-2.5-flash", "gemini-1.5-flash"]

    for model_name in models_to_try:
        endpoint = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
        
        # ট্রাফিক বা হাই ডিমান্ড ওভারলোড সামলানোর জন্য চেষ্টার সংখ্যা বাড়িয়ে দেওয়া হলো
        for attempt in range(1, 4):
            try:
                print(f"🤖 Trying Model: {model_name} (Attempt {attempt})...")
                response = requests.post(endpoint, json=payload, timeout=50)
                res_json = response.json()
                
                if response.status_code == 200:
                    if 'candidates' in res_json and res_json['candidates']:
                        text = res_json['candidates'][0]['content']['parts'][0]['text']
                        print(f"✅ Successfully generated content using {model_name}")
                        return text
                else:
                    err_msg = res_json.get('error', {}).get('message', 'Unknown Error')
                    print(f"⚠️ API Error ({response.status_code}) [{model_name}]: {err_msg}")
                    
                    # যদি সার্ভার ওভারলোড (503) বা হাই ডিমান্ড বা রেট লিমিট হয়, তবে একটু বেশি সময় অপেক্ষা করে আবার ট্রাই করবে
                    if response.status_code == 503 or "rate limit" in err_msg.lower() or "quota" in err_msg.lower():
                        print(f"⏳ Server busy or high demand. Waiting 15 seconds before retry...")
                        time.sleep(15)
                    else:
                        time.sleep(5)
                        break # অন্য মডেল ট্রাই করার জন্য লুপ ব্রেক করা
                        
            except Exception as e:
                print(f"⚠️ Exception with {model_name}: {e}")
                time.sleep(5)

    raise Exception("❌ Gemini API failed due to high demand or network issues. Please try running workflow again.")
