import re


def clean_text(text):
    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()



def optimize_seo(title, content, category):

    title = clean_text(title)

    content_text = clean_text(
        content
    )


    # Primary keyword
    primary_keyword = title.lower()


    # Word count
    word_count = len(
        content_text.split()
    )


    # Search Description (150-160 character target)
    search_description = (
        f"{title} সম্পর্কে সম্পূর্ণ বাংলা গাইড। "
        f"জানুন বিস্তারিত তথ্য, সুবিধা, ব্যবহার এবং প্রয়োজনীয় টিপস।"
    )


    search_description = search_description[:160]


    # Related keywords
    keywords = [
        title,
        category,
        "বাংলা টেক গাইড",
        "Technology Guide 2026",
        "TechBangla"
    ]


    # SEO report
    seo_data = {

        "primary_keyword": primary_keyword,

        "keywords": keywords,

        "search_description": search_description,

        "word_count": word_count,

        "seo_check": {

            "title_length":
                len(title),

            "content_length":
                word_count,

            "has_h2":
                "<h2>" in content,

            "has_h3":
                "<h3>" in content

        }
    }


    return seo_data