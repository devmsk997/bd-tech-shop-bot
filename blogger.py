import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_blogger_service():
    # গিটহাব সিক্রেটস থেকে বিভিন্ন নামে থাকা ক্রেডেনশিয়াল চেক করা
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON") or os.getenv("GOOGLE_TOKEN_JSON") or os.getenv("BLOGGER_CREDENTIALS")
    
    if not creds_json:
        raise ValueError("❌ ব্লগার এপিআই ক্রেডেনশিয়াল এনভায়রনমেন্ট ভেরিয়েবলে পাওয়া যায়নি!")

    try:
        if isinstance(creds_json, str):
            creds_info = json.loads(creds_json)
        else:
            creds_info = creds_json

        # ওঅথ টোকেন ফরম্যাট যাচাই করা
        creds = Credentials.from_authorized_user_info(creds_info)
        service = build('blogger', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise Exception(f"❌ ব্লগার সার্ভিস তৈরি করতে সমস্যা হয়েছে। দয়া করে গিটহাব সিক্রেটসে সঠিক OAuth JSON টোকেন দিন। মূল এরর: {e}")

def publish_to_blogger(title, content, labels=None):
    service = get_blogger_service()
    blog_id = os.getenv("BLOG_ID") or os.getenv("BLOGGER_BLOG_ID")
    
    if not blog_id:
        raise ValueError("❌ ব্লগ আইডি (BLOG_ID) এনভায়রনমেন্ট ভেরিয়েবলে পাওয়া যায়নি!")

    # যদি লেবেল বা ক্যাটাগরি না দেওয়া হয়, তবে ডিফল্ট হিসেবে এই লেবেলগুলো ব্যবহার করবে
    if labels is None:
        labels = ["মোবাইল ও গ্যাজেট", "Tech Review", "BD Price"]

    body = {
        "title": title,
        "content": content,
        "labels": labels  # <--- এখানে ব্লগ পোস্টের লেবেল বা ক্যাটাগরি যুক্ত করা হলো
    }

    posts = service.posts()
    request = posts.insert(blogId=blog_id, body=body)
    response = request.execute()

    post_url = response.get('url')
    print(f"✅ সফলভাবে ব্লগে পোস্ট পাবলিশ হয়েছে! লিংক: {post_url}")
    return post_url
