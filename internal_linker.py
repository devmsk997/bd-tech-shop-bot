import json
import os

POST_FILE = "blog_posts.json"

def load_posts():
    if os.path.exists(POST_FILE):
        try:
            with open(POST_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []
    return []

def save_post(title, url, category="General"):
    posts = load_posts()
    
    # ডুপ্লিকেট চেক করে সেভ করা
    for post in posts:
        if post.get("url") == url or post.get("title") == title:
            return
    
    posts.append({
        "title": title,
        "url": url,
        "category": category
    })
    
    try:
        with open(POST_FILE, "w", encoding="utf-8") as file:
            json.dump(posts, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"⚠️ Error saving post to JSON: {e}")

def get_related_posts(category):
    posts = load_posts()
    # ক্যাটাগরি অনুযায়ী পোস্ট ফিল্টার করা, না মিললে সাম্প্রতিক পোস্টগুলো নেওয়া
    related = [p for p in posts if p.get("category") == category]
    if not related:
        related = posts
    return related[-5:]  # শেষ ৫টি পোস্ট রিটার্ন করবে

def add_internal_links(content, category="General"):
    try:
        posts = get_related_posts(category)
    except Exception:
        posts = []

    if not posts:
        return content

    links = """
<h2>আরও পড়ুন</h2>
<ul>
"""

    count = 0
    for post in posts:
        if count >= 5:
            break

        title = post.get('title')
        url = post.get('url')

        if title and url:
            links += f"""
<li>
<a href="{url}">
{title}
</a>
</li>
"""
            count += 1

    links += """
</ul>
"""

    if count == 0:
        return content

    return content + links
