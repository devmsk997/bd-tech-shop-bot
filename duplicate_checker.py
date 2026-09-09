import json
import os
from difflib import SequenceMatcher


POST_FILE = "blog_posts.json"



def load_posts():

    if os.path.exists(POST_FILE):

        with open(
            POST_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    return []





def clean_text(text):

    return (
        text
        .lower()
        .replace("\n"," ")
        .replace("<"," ")
        .replace(">"," ")
    )





def check_duplicate(title, content):


    posts = load_posts()


    new_text = clean_text(
        title + content
    )



    for post in posts:


        old_text = clean_text(

            post.get("title","")

        )



        similarity = SequenceMatcher(

            None,

            new_text,

            old_text

        ).ratio()



        if similarity > 0.70:


            return {

                "duplicate": True,

                "similarity": round(
                    similarity * 100,
                    2
                )

            }



    return {

        "duplicate": False,

        "similarity": 0

    }