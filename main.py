import os
from keyword_research import get_high_search_product
from gemini_writer import generate_seo_review
from blogger import publish_to_blogger
from github_image import get_working_image_url

AFFILIATE_TAG = "?ref=379372"

def main():
    print("🚀 Blogger Auto-Post Bot Started...")
    
    # ১. কিওয়ার্ড ও প্রোডাক্ট নির্বাচন
    product_data = get_high_search_product()
    title = product_data['title']
    raw_url = product_data['url']
    raw_image_url = product_data['image']
    
    # ২. ইমেজ ও অ্যাফিলিয়েট লিঙ্ক প্রসেস
    working_image_url = get_working_image_url(raw_image_url)
    affiliate_link = raw_url + AFFILIATE_TAG if "?" not in raw_url else raw_url + "&ref=379372"
    
    print(f"📦 Product Found: {title}")
    print(f"🖼️ Working Image URL: {working_image_url}")
    print(f"🔗 Affiliate Link: {affiliate_link}")
    
    # ৩. কন্টেন্ট তৈরি (Gemini API)
    review_html = generate_seo_review(title)
    
    # ৪. ব্লগার ফার্স্ট-ইমেজ ও থাম্বনেইল কমপ্যাটিবল লেআউট
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
    
    # ৫. ব্লগারে পোস্ট প্রকাশ
    blog_post_url = publish_to_blogger(title, formatted_content)
    print(f"✅ Successfully Published to Blogger: {blog_post_url}")

if __name__ == "__main__":
    main()
