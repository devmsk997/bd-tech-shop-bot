import os
import json
import time
import re
from google import genai
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# SEO & Bot Modules Import
from topic_cluster import choose_topic
from keyword_research import research_keywords
from gemini_writer import generate_article
from seo_optimizer import optimize_seo
from duplicate_checker import check_duplicate
from internal_linker import add_internal_links
from image_generator import generate_image
from github_image import upload_image
from blogger import create_json_ld, save_post

# Optional quality score check
try:
    from quality_score import calculate_quality_score
except ImportError:
    def calculate_quality_score(title, content):
        return {"score": 100}

# Environment Variables
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = os.environ.get("BLOG_ID")
CREDENTIALS_JSON = os.environ.get("GOOGLE_CREDENTIALS_JSON") or os.environ.get("CREDENTIALS_JSON")
TOKEN_JSON = os.environ.get("GOOGLE_TOKEN_JSON") or os.environ.get("TOKEN_JSON")

def get_blogger_service():
    token_data = json.loads(TOKEN_JSON)
    creds = Credentials.from_authorized_user_info(token_data)
    if creds and creds.expired and creds.refresh_token:
        client_data = json.loads(CREDENTIALS_JSON)
        creds.refresh(Request())
    return build('blogger', 'v3', credentials=creds)

def parse_gemini_output(generated_text):
    title_match = re.search(r"TITLE:\s*(.*?)\n", generated_text)
    desc_match = re.search(r"SEARCH_DESCRIPTION:\s*(.*?)\n", generated_text)
    labels_match = re.search(r"LABELS:\s*(.*?)\n", generated_text)
    content_match = re.search(r"CONTENT:\s*(.*)", generated_text, re.DOTALL)

    title = title_match.group(1).strip() if title_match else "BD Tech Shop Review"
    search_description = desc_match.group(1).strip() if desc_match else ""
    
    labels_raw = labels_match.group(1).strip() if labels_match else ""
    labels = [label.strip() for label in labels_raw.split(",") if label.strip()]
    
    content = content_match.group(1).strip() if content_match else generated_text
    return title, search_description, labels, content

def main():
    print("🚀 BD Tech Shop Review Auto-Post Bot Started")
    
    # 1. Topic & Category Selection
    topic, category = choose_topic()
    print(f"📌 Topic: {topic} | Category: {category}")

    # 2. Keyword Research
    keywords = research_keywords(category, topic)
    print(f"🔑 Keywords: {keywords}")

    # 3. Article Generation using Gemini
    raw_article = generate_article(topic, category, keywords)
    title, search_description, labels, content = parse_gemini_output(raw_article)

    # 4. Duplicate Check
    dup_res = check_duplicate(title, content)
    if dup_res.get("duplicate"):
        print(f"⚠️ Duplicate detected ({dup_res.get('similarity')}% similarity). Skipping generation.")
        return

    # 5. Quality & SEO Check
    q_score = calculate_quality_score(title, content)
    print(f"📊 Quality Score: {q_score['score']}/100")

    # 6. Internal Linking
    content = add_internal_links(content, category)

    # 7. Image Generation & Upload
    try:
        local_img = generate_image(title)
        img_url = upload_image(local_img) if local_img else None
    except Exception as e:
        print(f"Image generation skipped: {e}")
        img_url = None

    # 8. SEO Optimization Payload
    seo_data = optimize_seo(title, content, category)
    if not search_description:
        search_description = seo_data["search_description"]

    # 9. Format Content with Schema & Image
    try:
        schema = create_json_ld(title, search_description, img_url)
    except Exception:
        schema = ""
        
    image_html = f'<div style="text-align:center;"><img src="{img_url}" alt="{title}" style="max-width:100%;height:auto;"/></div><br/>' if img_url else ""
    final_content = schema + image_html + content

    # 10. Publish to Blogger
    blogger_service = get_blogger_service()
    body = {
        "kind": "blogger#post",
        "title": title,
        "content": final_content,
        "labels": labels if labels else [category],
        "searchDescription": search_description
    }

    res = blogger_service.posts().insert(blogId=BLOG_ID, body=body, isDraft=False).execute()
    print(f"✅ Successfully Published: {res.get('url')}")
    
    try:
        save_post(title, res.get('url'), category)
    except Exception:
        pass

if __name__ == "__main__":
    main()
