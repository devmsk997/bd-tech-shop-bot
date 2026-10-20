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
        .replace("price in bangladesh", "")
        .replace("review 2026", "")
        .replace("price", "")
        .replace("review", "")
        .replace("-", " ")
        .replace("|", " ")
        .replace("\n", " ")
        .strip()
    )

def check_duplicate(title, product_url=""):
    posts = load_posts()
    cleaned_new_title = clean_text(title)

    for post in posts:
        old_title = post.get("title", "")
        old_url = post.get("url", "")
        
        # ১. যদি প্রোডাক্টের URL হুবহু মিলে যায়, তবে নিশ্চিতভাবে ডুপ্লিকেট
        if product_url and old_url and product_url.strip() == old_url.strip():
            return {
                "duplicate": True,
                "similarity": 100.0
            }

        cleaned_old_title = clean_text(old_title)

        # টাইটেলের মিল কতটুকু তা মাপা
        title_similarity = SequenceMatcher(None, cleaned_new_title, cleaned_old_title).ratio()

        # থ্রেশহোল্ড ৬০% থেকে বাড়িয়ে ৮৫% করা হয়েছে, যাতে একই ব্র্যান্ডের অন্য মডেলের প্রোডাক্ট ডুপ্লিকেট না ধরে
        if title_similarity > 0.85:
            return {
                "duplicate": True,
                "similarity": round(title_similarity * 100, 2)
            }

    return {
        "duplicate": False,
        "similarity": 0
    }
