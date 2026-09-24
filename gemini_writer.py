import os
import time
from google import genai
from optimize_seo import optimize_seo

def generate_seo_review(title, category="Tech"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("❌ GEMINI_API_KEY is missing in environment variables!")

    # Google GenAI ক্লায়েন্ট ইনিশিয়ালাইজ করা
    client = genai.Client(api_key=api_key)

    prompt = f"""
Create a comprehensive, highly engaging SEO-optimized product review in Bengali for: "{title}".
Write in professional markdown / HTML format (suitable for Blogger). 
Ensure the content includes an introduction, key specifications/features, pros and cons, why you should buy it, and a conclusion.
Make sure to use <h2> and <h3> tags for subheadings.
"""

    # বর্তমানে কাজ করার মতো সঠিক মডেল আইডি ব্যবহার করা
    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro"]
    
    response = None
    selected_model = ""

    for model_name in models_to_try:
        for attempt in range(1, 4):
            try:
                print(f"🤖 Requesting API using model: {model_name} (Attempt {attempt})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                if response and response.text:
                    selected_model = model_name
                    break
            except Exception as e:
                print(f"⚠️ API Error with {model_name}: {e}")
                time.sleep(5)
        if response and response.text:
            break

    if not response or not response.text:
        raise Exception("❌ Gemini API failed across all available models after retries.")

    print(f"✅ Successfully generated content using model: {selected_model}")
    return response.text
