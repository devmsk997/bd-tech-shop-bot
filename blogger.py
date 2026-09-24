import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_blogger_service():
    # এনভায়রনমেন্ট ভেরিয়াবেল থেকে টোকেন বা ক্রেডেনশিয়াল রিড করা
    creds_json = os.getenv("BLOGGER_CREDENTIALS") or os.getenv("GCP_CREDENTIALS")
    
    if not creds_json:
        raise ValueError("❌ Blogger credentials missing in environment variables!")

    try:
        # JSON স্ট্রিংকে ডিকশনারিতে রূপান্তর
        if isinstance(creds_json, str):
            creds_info = json.loads(creds_json)
        else:
            creds_info = creds_json

        # সঠিক নিয়মে Credentials তৈরি করা (কোনো কিওয়ার্ড আর্গুমেন্ট ছাড়া)
        creds = Credentials.from_authorized_user_info(creds_info)
        
        service = build('blogger', 'v3', credentials=creds)
        return service
    except Exception as e:
        raise Exception(f"❌ Failed to create Blogger service: {e}")

def publish_to_blogger(title, content):
    try:
        service = get_blogger_service()
        blog_id = os.getenv("BLOGGER_BLOG_ID")
        
        if not blog_id:
            raise ValueError("❌ BLOGGER_BLOG_ID is missing in environment variables!")

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

    except Exception as e:
        print(f"❌ Blogger Publishing Error: {e}")
        return None
