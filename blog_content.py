import json
import os


POSTS_FILE = "blog_posts.json"



def load_posts():

    if os.path.exists(POSTS_FILE):

        try:

            with open(
                POSTS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)


        except Exception:

            return []


    return []





def save_post(title, url, category):

    posts = load_posts()



    # Duplicate check

    for post in posts:

        if post.get("url") == url:

            return



    posts.append({

        "title": title,

        "url": url,

        "category": category

    })



    with open(
        POSTS_FILE,
        "w",
        encoding="utf-8"
    ) as file:


        json.dump(

            posts,

            file,

            ensure_ascii=False,

            indent=4

        )







def get_related_posts(category):


    posts = load_posts()


    related = []



    for post in posts:


        if (

            post.get("category") == category

            and post.get("title")

            and post.get("url")

        ):


            related.append(post)



    return related[:5]







def create_internal_links(category):


    related = get_related_posts(category)



    if not related:

        return ""




    html = """

<h2>আরও পড়ুন</h2>

<ul>

"""



    for post in related:


        html += f"""

<li>

<a href="{post['url']}">

{post['title']}

</a>

</li>

"""



    html += """

</ul>

"""



    return html