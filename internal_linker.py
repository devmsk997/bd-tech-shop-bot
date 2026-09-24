from blog_content import get_related_posts

def add_internal_links(content, category):
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

        # নিশ্চিত করা হচ্ছে যে টাইটেল এবং ইউআরএল উভয়ই উপস্থিত আছে
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

    # যদি কোনো ভ্যালিড লিংক না পাওয়া যায়, তবে শুধু মূল কনটেন্ট রিটার্ন করবে
    if count == 0:
        return content

    return content + links
