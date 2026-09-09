from blog_content import get_related_posts


def add_internal_links(content, category):

    posts = get_related_posts(category)


    if not posts:
        return content



    links = """

<h2>আরও পড়ুন</h2>

<ul>

"""


    count = 0


    for post in posts:

        if count >= 5:
            break


        links += f"""

<li>
<a href="{post['url']}">
{post['title']}
</a>
</li>

"""


        count += 1



    links += """

</ul>

"""



    return content + links