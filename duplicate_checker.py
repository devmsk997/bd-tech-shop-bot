import json
import os
from difflib import SequenceMatcher

POST_FILE = "blog_posts.json"

def load_posts():
    if os.path.exists(POST_FILE):
        try:
            with open(POST_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception:
            return []
    return []

def clean_text(text):
    if not text:
        return ""
    return (
        text
        .lower()
        .replace("\n", " ")
        .replace("<", " ")
        .replace(">", " ")
    )

def check_duplicate(title, content=""):
    posts = load_posts()
    new_text = clean_text(title + " " + content)

    for post in posts:
        old_title = post.get("title", "")
        old_text = clean_text(old_title)

        # ওভারঅল টেক্সট এবং শুধু টাইটেলের মিল চেক করা
        similarity = SequenceMatcher(None, new_text, old_text).ratio()
        title_similarity = SequenceMatcher(None, clean_text(title), old_text).ratio()

        # যদি সিমিলারিটি ৭০% এর বেশি হয়, তবে ডুপ্লিকেট হিসেবে ধরবে
        if similarity > 0.70 or title_similarity > 0.85:
            return {
                "duplicate": True,
                "similarity": round(max(similarity, title_similarity) * 100, 2)
            }

    return {
        "duplicate": False,
        "similarity": 0
    }
