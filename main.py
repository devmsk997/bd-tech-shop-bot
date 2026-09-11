import os
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# GitHub Secrets থেকে Gemini API Key নেওয়া হবে
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# আপনার BDStall অ্যাফিলিয়েট রেফারেল আইডি
AFFILIATE_TAG = "?ref=379372"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')

def fetch_bdstall_product():
    """BDStall থেকে প্রোডাক্টের তথ্য, ছবি ও লিঙ্ক সংগ্রহ করে"""
    url = "https://www.bdstall.com/technology/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    product = soup.find('div', class_='product-spec') 
    title = product.find('h2').text.strip()
    raw_link = "https://www.bdstall.com" + product.find('a')['href']
    image_url = product.find('img')['src']
    
    # অ্যাফিলিয়েট আইডি যুক্ত লিঙ্ক
    affiliate_link = raw_link + AFFILIATE_TAG
    return title, image_url, affiliate_link

def generate_review(title):
    """Gemini AI দিয়ে বাংলা রিভিউ পোস্ট ক্যাপশন তৈরি করে"""
    prompt = f"""
    একটি টেক পেজের জন্য চমৎকার বাংলা রিভিউ পোস্ট ক্যাপশন লিখুন:
    প্রোডাক্টের নাম: {title}
    
    পোস্টের গঠন:
    ১. আকর্ষনীয় শীরোনাম (ইমোজি সহ)
    ২. ৩-৪টি প্রধান ফিচার/সুবিধা (বুলেট পয়েন্টে)
    ৩. কেন এই প্রোডাক্টটি কেনা উচিত (১-২ লাইন)
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    print("🚀 BDStall Feature Image সহ রিভিউ জেনারেটর চালু হয়েছে...\n")
    try:
        title, image_url, affiliate_link = fetch_bdstall_product()
        caption = generate_review(title)
        
        # জেনারেট হওয়া সম্পূর্ণ পোস্ট
        print("================ 📝 জেনারেট হওয়া পোস্ট ================")
        print(caption)
        print("\n------------------------------------------------------")
        print(f"🖼️ প্রোডাক্টের ফিচারড ইমেজ (Featured Image URL): {image_url}")
        print(f"🛒 অ্যাফিলিয়েট অর্ডারিং লিংক: {affiliate_link}")
        print("======================================================")
        
    except Exception as e:
        print(f"⚠️ ত্রুটি দেখা দিয়েছে: {e}")

if __name__ == "__main__":
    main()
