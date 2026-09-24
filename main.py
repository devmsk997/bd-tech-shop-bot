import os
import requests
from keyword_research import get_high_search_product
from gemini_writer import generate_seo_review
from blogger import publish_to_blogger
from github_image import get_working_image_url
from duplicate_checker import check_duplicate
from internal_linker import save_post

AFFILIATE_TAG = "?ref=379372"

# ফেসবুক পেজে পোস্ট করার ফাংশন
def post_to_facebook(title, blog_url, image_url):
    app_id = os.getenv("FB_APP_ID")
    app_secret = os.getenv("FB_APP_SECRET")
    page_id = os.getenv("FB_PAGE_ID")
    
    if not all([app_id, app_secret, page_id]):
        print("⚠️ Facebook credentials missing in environment variables!")
        return

    try:
        # ১. App Access Token জেনারেট করা
        token_url = f"https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={app_secret}&grant_type=client_credentials"
        token_res = requests.get(token_url)
        access_token = token_res.json().get("access_token")
        
        if not access_token:
            print("❌ Failed to generate Facebook Access Token.")
            return

        # ২. ফেসবুক পেজে পোস্ট পাঠানো
        post_url = f"https://graph.facebook.com/v26.0/{page_id}/feed"
        message = f"🔥 নতুন রিভিউ: {title}\n\nবিস্তারিত পড়ুন এবং অফারটি দেখতে ক্লিক করুন:\n{blog_url}"
        
        payload = {
            'message': message,
            'link': blog_url,
            'access_token': access_token
        }
        
        response = requests.post(post_url, data=payload)
        res_data = response.json()
        
        if 'id' in res_data:
            print(f"✅ Successfully Posted to Facebook Page! Post ID: {res_data['id']}")
        else:
            print(f"❌ Failed to post on Facebook: {res_data}")
            
    except Exception as e:
        print(f"❌ Error posting to Facebook: {e}")

def main():
    print("🚀 Blogger Auto-Post Bot Started...")
    
    # শতভাগ ইউনিক এবং লেটেস্ট প্রোডাক্ট খোঁজার জন্য উন্নত লুপ (সর্বোচ্চ ১০ বার চেষ্টা করবে)
    product_data = None
    for attempt in range(1, 11):
        temp_product = get_high_search_product()
        if not temp_product or 'title' not in temp_product:
            continue
            
        temp_title = temp_product['title']
        
        # ডুপ্লিকেট চেক করা
        dup_check = check_duplicate(temp_title, "")
        if not dup_check["duplicate"]:
            product_data = temp_product
            print(f"✨ ইউনিক প্রোডাক্ট পাওয়া গেছে (চেষ্টা {attempt}): {temp_title}")
            break
        else:
            print(f"🔄 ডুপ্লিকেট পাওয়া গেছে '{temp_title}' ({dup_check['similarity']}% মিল)। অন্য প্রোডাক্ট খোঁজা হচ্ছে...")

    # যদি ১০ বার চেষ্টার পরও শতভাগ ইউনিক না পাওয়া যায়, তবে আগের কোডের মতো জোর করে না চালিয়ে সেফলি প্রসেস বন্ধ করবে যাতে ডুপ্লিকেট পোস্ট না হয়
    if not product_data:
        print("❌ দুঃখিত, বর্তমানে কোনো নতুন ইউনিক প্রোডাক্ট পাওয়া যায়নি। ডুপ্লিকেট এড়াতে আজকের পোস্ট বাতিল করা হলো।")
        return

    title = product_data['title']
    raw_url = product_data['url']
    raw_image_url = product_data['image']
    
    # ইমেজ ও অ্যাফিলিয়েট লিঙ্ক প্রসেস
    working_image_url = get_working_image_url(raw_image_url, title)
    affiliate_link = raw_url + AFFILIATE_TAG if "?" not in raw_url else raw_url + "&ref=379372"
    
    print(gz := f"📦 Selected Unique Product: {title}")
    print(f"🖼️ Working Image URL: {working_image_url[:60]}...")
    print(f"🔗 Affiliate Link: {affiliate_link}")
    
    # কন্টেন্ট তৈরি (Gemini API)
    review_html = generate_seo_review(title)
    
    # ব্লগার ফিচারড ইমেজ লেআউট
    featured_img_tag = f"""
    <div class="separator" style="clear: both; text-align: center; margin-top: 10px; margin-bottom: 25px;">
        <a href="{affiliate_link}" target="_blank" rel="nofollow sponsored" style="margin-left: 1em; margin-right: 1em;">
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
    
    # ব্লগারে পোস্ট প্রকাশ
    blog_post_url = publish_to_blogger(title, formatted_content)
    
    if blog_post_url:
        print(f"✅ Successfully Published to Blogger: {blog_post_url}")
        
        # সফলভাবে পোস্ট হওয়ার পর লোকাল JSON ফাইলে রেকর্ড সেভ করা (যাতে ভবিষ্যতে ডুপ্লিকেট না হয়)
        save_post(title, blog_post_url, "মোবাইল ও গ্যাজেট")
        
        # ফেসবুক পেজে অটো-পোস্ট করা
        print("📢 Publishing to Facebook Page...")
        post_to_facebook(title, blog_post_url, working_image_url)
    else:
        print("❌ Failed to publish post to Blogger.")

if __name__ == "__main__":
    main()
