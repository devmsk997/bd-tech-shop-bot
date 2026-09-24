import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_blogger_service():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON") or os.getenv("BLOGGER_CREDENTIALS")
    
    if not creds_json:
        raise ValueError("❌ Blogger credentials missing in environment variables!")

    try:
        if isinstance(creds_json, str):
            creds_info = json.loads(creds_json)
        else:
            creds_info = creds_json

        creds = Credentials.from_authorized_user_info(creds_info)
        service = build('blogger', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise Exception(f"❌ Failed to create Blogger service: {e}")

def publish_to_blogger(title, content):
    service = get_blogger_service()
    # আপনার গিটহাব সিক্রেটসে থাকা নাম (BLOG_ID) এখানে যুক্ত করা হলো
    blog_id = os.getenv("BLOG_ID") or os.getenv("BLOGGER_BLOG_ID")
    
    if not blog_id:
        raise ValueError("❌ BLOG_ID is missing in environment variables!")

    body = {
        "title": title,
        "content": content
    }

    posts = service.posts()
    request = posts.insert(blogId=blog_id, body=body)
    response = request.execute()

    post_url = response.get('url')
    print(f"✅ Successfully Published to Blogger! URL: {post_url}")
    return post_url
