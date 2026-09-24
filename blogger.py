import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON")

def get_blogger_service():
    if not TOKEN_JSON:
        raise ValueError("❌ GOOGLE_TOKEN_JSON environment variable is missing!")
    
    token_data = json.loads(TOKEN_JSON)
    
    # ক্লায়েন্ট আইডি এবং সিক্রেট এক্সট্রাক্ট করা (যদি ক্রেডেনশিয়াল JSON থাকে)
    client_id = None
    client_secret = None
    if CREDENTIALS_JSON:
        try:
            creds_data = json.loads(CREDENTIALS_JSON)
            # সাধারণত এটি 'installed' বা 'web' এর ভেতরে থাকে
            key_type = 'installed' if 'installed' in creds_data else 'web'
            client_id = creds_data.get(key_type, {}).get('client_id')
            client_secret = creds_data.get(key_type, {}).get('client_secret')
        except Exception:
            pass

    creds = Credentials.from_authorized_user_info(
        token_data, 
        client_id=client_id, 
        client_secret=client_secret
    )
    
    # টোকেন এক্সপায়ার্ড হলে তা রিফ্রেশ করা
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"⚠️ Token refresh warning: {e}")
            
    return build('blogger', 'v3', credentials=creds)

def publish_to_blogger(title, formatted_content, labels=["Tech Review", "BDStall"]):
    blogger_service = get_blogger_service()
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": formatted_content,
        "labels": labels
    }
    
    # সরাসরি পাবলিশ নিশ্চিত করা হচ্ছে
    res = blogger_service.posts().insert(
        blogId=BLOG_ID, 
        body=body, 
        isDraft=False
    ).execute()
    
    return res.get('url')
