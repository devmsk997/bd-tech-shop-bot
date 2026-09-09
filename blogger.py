from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import os
import json
from datetime import datetime

from config import BLOG_ID
from blog_content import save_post



SCOPES = [
    "https://www.googleapis.com/auth/blogger"
]



def get_service():

    creds = None


    if os.path.exists("token.json"):

        creds = Credentials.from_authorized_user_file(
            "token.json",
            SCOPES
        )


    if not creds or not creds.valid:


        flow = InstalledAppFlow.from_client_secrets_file(

            "credentials.json",

            SCOPES

        )


        creds = flow.run_local_server(
            port=0
        )


        with open(
            "token.json",
            "w"
        ) as token:

            token.write(
                creds.to_json()
            )



    return build(
        "blogger",
        "v3",
        credentials=creds
    )







def create_json_ld(

        title,

        description,

        image_url

):


    schema = {


        "@context":

        "https://schema.org",



        "@type":

        "Article",



        "headline":

        title,



        "description":

        description,



        "image":

        [

            image_url

        ] if image_url else [],




        "author":

        {

            "@type":

            "Organization",


            "name":

            "TechBangla"

        },




        "publisher":

        {

            "@type":

            "Organization",


            "name":

            "TechBangla",


            "logo":

            {

                "@type":

                "ImageObject",


                "url":

                "https://blogger.googleusercontent.com/img/b/R29vZ2xl/"

            }

        },




        "datePublished":

        datetime.now().isoformat(),




        "mainEntityOfPage":

        {

            "@type":

            "WebPage",

            "@id":

            "https://techbangla996.blogspot.com"

        }


    }



    return f"""

<script type="application/ld+json">

{json.dumps(schema, ensure_ascii=False)}

</script>

"""








def create_post(

        title,

        content,

        labels=None,

        search_description=None,

        image_url=None

):


    service = get_service()



    schema = create_json_ld(

        title,

        search_description,

        image_url

    )




    image_html = ""



    if image_url:


        image_html = f"""

<div class="separator"

style="clear: both; text-align:center;">


<img

src="{image_url}"

alt="{title}"

title="{title}"

loading="eager"

width="1200"

height="675"

style="max-width:100%;height:auto;">


</div>

<br/>

"""





    final_content = (

        schema

        + image_html

        + content

    )





    post = {


        "kind":

        "blogger#post",



        "title":

        title,



        "content":

        final_content

    }




    if labels:

        post["labels"] = labels




    if search_description:

        post["searchDescription"] = search_description






    result = service.posts().insert(


        blogId=BLOG_ID,


        body=post,


        isDraft=False


    ).execute()





    print("Published:")

    print(result["url"])





    save_post(

        title,

        result["url"],

        labels[0] if labels else "Technology"

    )