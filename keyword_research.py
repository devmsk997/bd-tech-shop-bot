import random


KEYWORD_DATABASE = {

    "সাইবার নিরাপত্তা": [
        "cyber security tips",
        "online security",
        "password protection",
        "phishing protection",
        "data privacy"
    ],


    "AI টুলস": [
        "best AI tools",
        "AI productivity tools",
        "AI automation",
        "AI technology"
    ],


    "মোবাইল টিপস": [
        "android tips",
        "phone optimization",
        "smartphone security"
    ],


    "অ্যাপস": [
        "best android apps",
        "useful mobile apps",
        "app security"
    ],


    "টেক নিউজ": [
        "latest technology news",
        "AI news",
        "Google updates"
    ]

}



def research_keywords(category, topic):


    keywords = KEYWORD_DATABASE.get(

        category,

        []

    )


    primary = topic.lower()



    related = random.sample(

        keywords,

        min(
            3,
            len(keywords)
        )

    )



    return {

        "primary_keyword": primary,

        "related_keywords": related

    }