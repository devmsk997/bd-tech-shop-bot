import os
import json

# config বাদ দিয়ে সরাসরি Environment Variables থেকে BLOG_ID রিড করা
BLOG_ID = os.environ.get("BLOG_ID")

def create_json_ld(title, description, image_url=None):
    schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": title,
        "description": description,
        "mainEntityOfPage": {
            "@type": "WebPage"
        }
    }
    if image_url:
        schema["image"] = [image_url]
        
    return f'<script type="application/ld+json">\n{json.dumps(schema, ensure_ascii=False, indent=2)}\n</script>\n'

def save_post(title, url, category):
    file_name = "blog_posts.json"
    posts = []
    
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                posts = json.load(f)
        except Exception:
            posts = []
            
    posts.append({
        "title": title,
        "url": url,
        "category": category
    })
    
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
