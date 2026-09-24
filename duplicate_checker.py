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
    # অপ্রয়োজনীয় শব্দ, হাইফেন বা স্পেশাল ক্যারেক্টার দূর করে শুধু মূল শব্দগুলো রাখা
    return (
        text
        .lower()
        .replace("price in bangladesh", "")
        .replace("review 2026", "")
        .replace("price", "")
        .replace("review", "")
        .replace("-", " ")
        .replace("|", " ")
        .replace("\n", " ")
        .strip()
    )

def check_duplicate(title, content=""):
    posts = load_posts()
    cleaned_new_title = clean_text(title)

    for post in posts:
        old_title = post.get("title", "")
        cleaned_old_title = clean_text(old_title)

        # শুধু টাইটেলের মধ্যে মিল কতটুকু তা মাপা
        title_similarity = SequenceMatcher(None, cleaned_new_title, cleaned_old_title).ratio()

        # যদি টাইটেলের মিল ৬০% বা তার বেশি হয়, তবে ডুপ্লিকেট হিসেবে ধরবে (যাতে একই ফোনের অন্য কোনো রিভিউ ডাবল পোস্ট না হয়)
        if title_similarity > 0.60:
            return {
                "duplicate": True,
                "similarity": round(title_similarity * 100, 2)
            }

    return {
        "duplicate": False,
        "similarity": 0
    }
