import requests
import base64
import os
import time

from config import (
    GITHUB_TOKEN,
    GITHUB_USERNAME,
    GITHUB_REPO
)



def check_image_url(url):

    try:

        response = requests.get(
            url,
            timeout=15
        )


        if response.status_code == 200:

            return True


        return False



    except Exception:

        return False






def upload_image(image_file):

    if not image_file:

        return None



    if not os.path.exists(image_file):

        print(
            "Image not found:",
            image_file
        )

        return None



    try:


        with open(
            image_file,
            "rb"
        ) as file:


            image_data = base64.b64encode(
                file.read()
            ).decode("utf-8")





        filename = (

            "images/featured_"

            + str(int(time.time()))

            + ".jpg"

        )





        api_url = (

            f"https://api.github.com/repos/"

            f"{GITHUB_USERNAME}/"

            f"{GITHUB_REPO}/contents/"

            f"{filename}"

        )





        headers = {


            "Authorization":

            f"Bearer {GITHUB_TOKEN}",


            "Accept":

            "application/vnd.github+json",


            "X-GitHub-Api-Version":

            "2022-11-28"


        }





        data = {


            "message":

            "Upload featured image",


            "content":

            image_data


        }





        response = requests.put(

            api_url,

            headers=headers,

            json=data

        )





        if response.status_code not in [200,201]:


            print(

                "GitHub upload failed:",

                response.text

            )


            return None





        raw_url = (

            f"https://raw.githubusercontent.com/"

            f"{GITHUB_USERNAME}/"

            f"{GITHUB_REPO}/main/"

            f"{filename}"

        )





        print(

            "Checking GitHub image..."

        )





        time.sleep(3)





        if check_image_url(raw_url):


            print(

                "GitHub Image Verified:",

                raw_url

            )


            return raw_url





        else:


            print(

                "GitHub image verification failed"

            )


            return None





    except Exception as e:


        print(

            "GitHub image error:",

            e

        )


        return None