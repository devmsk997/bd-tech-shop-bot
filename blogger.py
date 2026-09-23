import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON")

def get_blogger_service():
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

def publish_to_blogger(title, formatted_content, labels=["Tech Review", "BDStall"]):
    blogger_service = get_blogger_service()
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": formatted_content,
        "labels": labels
    }
    # isDraft=False দিয়ে সরাসরি পাবলিশ নিশ্চিত করা হচ্ছে
    res = blogger_service.posts().insert(
        blogId=BLOG_ID, 
        body=body, 
        isDraft=False
    ).execute()
    
    return res.get('url')
