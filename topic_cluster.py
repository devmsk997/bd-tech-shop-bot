import json
import os
import random


POST_FILE = "posted_topics.json"



TOPIC_CLUSTERS = {

    "সাইবার নিরাপত্তা": [
        "Password Security",
        "Phishing",
        "OTP Scam",
        "2FA",
        "Malware",
        "Ransomware",
        "VPN",
        "Deepfake",
        "Passkey",
        "Password Manager",
        "Data Breach"
    ],

    "AI টুলস": [
        "ChatGPT",
        "AI Tools",
        "AI Productivity",
        "AI Image Generator",
        "AI Security"
    ],

    "মোবাইল টিপস": [
        "Android Tips",
        "Battery Optimization",
        "Phone Performance",
        "Smartphone Security"
    ],

    "অ্যাপস": [
        "Best Android Apps",
        "Useful Apps",
        "App Security"
    ],

    "টেক নিউজ": [
        "AI News",
        "Google Updates",
        "Technology Updates"
    ]
}



def load_previous():

    if os.path.exists(POST_FILE):

        try:

            with open(
                POST_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                return json.load(file)

        except:

            return []


    return []





def save_topic(topic):

    old = load_previous()

    if topic not in old:

        old.append(topic)


    with open(
        POST_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            old,
            file,
            ensure_ascii=False,
            indent=4
        )





def choose_topic():


    old_topics = load_previous()



    available = []



    for category, topics in TOPIC_CLUSTERS.items():

        for topic in topics:

            if topic not in old_topics:

                available.append(
                    (
                        topic,
                        category
                    )
                )



    # সব topic শেষ হলে reset

    if not available:


        old_topics = []


        with open(
            POST_FILE,
            "w",
            encoding="utf-8"
        ) as file:


            json.dump(
                [],
                file
            )


        for category, topics in TOPIC_CLUSTERS.items():

            for topic in topics:

                available.append(
                    (
                        topic,
                        category
                    )
                )




    topic, category = random.choice(
        available
    )



    save_topic(topic)



    return topic, category