import os
import time
from google import genai
from google.genai.errors import APIError

def generate_seo_review(title):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY is missing in environment variables!")

    # অফিসিয়াল Google GenAI ক্লায়েন্ট ইনিশিয়ালাইজ করা
    client = genai.Client(api_key=api_key)

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

    # গুগল জেমিনির বর্তমান রিকমেন্ডেড ও লেটেস্ট মডেল স্ট্রিং
    model_name = "gemini-3.6-flash"

    for attempt in range(1, 5):
        try:
            print(f"🤖 Requesting via Official GenAI SDK using {model_name} (Attempt {attempt})...")
            
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            
            if response and response.text:
                print(f"✅ Successfully generated content using {model_name}")
                return response.text
                
        except APIError as e:
            print(f"⚠️ Gemini API Error (Code {e.code}): {e.message}")
            if e.code == 503 or "high demand" in str(e).lower():
                print(f"⏳ Server high demand (503). Waiting 20 seconds before retry...")
                time.sleep(20)
            else:
                time.sleep(10)
        except Exception as e:
            print(f"⚠️ Unexpected Error: {e}")
            time.sleep(10)

    raise Exception("❌ Gemini API failed repeatedly due to high demand. Please try running the workflow again later.")
