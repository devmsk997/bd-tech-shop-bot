import os
import time
from google import genai
from google.genai.errors import APIError

def generate_seo_review(title):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ জেমিনি এপিআই কি (API Key) এনভায়রনমেন্ট ভেরিয়েবলে পাওয়া যায়নি!")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    আপনি একজন এসইও (SEO) বাংলা টেক ব্লগ রাইটার। নিচের প্রোডাক্টটির জন্য একটি সংক্ষিপ্ত ও আকর্ষণীয় রিভিউ পোস্ট লিখুন।
    প্রডাক্টের নাম: {title}
    
    গুরুত্বপূর্ণ নিয়মাবলী:
    ১. কোনো অবস্থাতেই স্টার (*) বা হ্যাশ (#) চিহ্ন ব্যবহার করবেন না।
    ২. ফরম্যাটিংয়ের জন্য কেবল এইচটিএমএল ট্যাগ (<h2>, <h3>, <b>, <ul>, <li>) ব্যবহার করুন।
    ৩. নিচের সেকশনগুলো সাজিয়ে লিখুন:
        - <h2>{title} এর বিস্তারিত স্পেসিফিকেশন</h2>
        - <h2>কেন এই প্রোডাক্টটি কেনা উচিত?</h2>
        - <h2>বাংলাদেশে {title} এর দাম ও বাজারের অবস্থা</h2>
        - <h2>আমাদের চূড়ান্ত মতামত</h2>
    """

    # ফ্রি এবং সচল মডেলগুলোর তালিকা (একটি ফেইল করলে অন্যটি কাজ করবে)
    free_models = [
        "gemini-2.5-flash",
        "gemini-3.6-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash"
    ]

    # পার্মানেন্ট সমাধানের জন্য ফলব্যাক লুপ (যতক্ষণ না সফল হয়, চেষ্টা চালিয়ে যাবে)
    for cycle in range(1, 4):  # পুরো লিস্টে সর্বোচ্চ ৩ বার সাইকেল ঘুরে চেষ্টা করবে
        for model_name in free_models:
            for attempt in range(1, 3): # প্রতিটি মডেলে ২ বার করে চেষ্টা
                try:
                    print(f"🤖 ফ্রি মডেল টেস্ট করা হচ্ছে: {model_name} (সাইকেল {cycle}, চেষ্টা {attempt})...")
                    
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    
                    if response and response.text:
                        print(f"✅ সফল! {model_name} মডেল ব্যবহার করে কন্টেন্ট তৈরি করা হয়েছে।")
                        return response.text
                        
                except APIError as e:
                    print(f"⚠️ এপিআই এরর - {model_name} (কোড {e.code}): {e.message}")
                    if e.code == 503 or "high demand" in str(e).lower():
                        print(f"⏳ সার্ভার ব্যস্ত (503)। ৫ সেকেন্ড অপেক্ষা করে পরবর্তী ধাপে যাওয়া হচ্ছে...")
                        time.sleep(5)
                    else:
                        time.sleep(2)
                        break 
                except Exception as e:
                    print(f"⚠️ অপ্রত্যাশিত সমস্যা {model_name} এ: {e}")
                    time.sleep(2)
                    break

        print(f"🔄 সাইকেল {cycle} সম্পন্ন হয়েছে। পুনরায় চেষ্টা করা হচ্ছে...")
        time.sleep(5)

    raise Exception("❌ বর্তমানে সমস্ত ফ্রি মডেল অতিরিক্ত ব্যস্ত রয়েছে। দয়া করে কিছুক্ষণ পর আবার গিটহাব অ্যাকশন রান করুন।")
