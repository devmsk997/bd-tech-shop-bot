from google import genai
import time

from config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODELS = [
    "gemini-3.6-flash"
]


MAX_RETRY = 5


def generate_article(topic, category, keywords):

    primary_keyword = keywords.get(
        "primary_keyword",
        topic
    )

    related_keywords = keywords.get(
        "related_keywords",
        []
    )

    prompt = f"""

আপনি TechBangla-এর জন্য একজন professional SEO বাংলা Technology writer।

Topic:
{topic}

Category:
{category}

Primary Keyword:
{primary_keyword}

Related Keywords:
{related_keywords}

আপনাকে অবশ্যই নিচের format অনুসরণ করতে হবে।

TITLE:
SEO friendly বাংলা title লিখুন।

SEARCH_DESCRIPTION:
150-160 character এর description লিখুন।

LABELS:
৩-৫টি label comma দিয়ে লিখুন।

CONTENT:
এর পরে HTML format-এ সম্পূর্ণ article লিখুন।

Rules:

- বাংলা ভাষায় লিখুন
- Unique content লিখুন
- 1500+ শব্দ
- SEO friendly করুন
- H2 H3 heading ব্যবহার করুন
- FAQ section যোগ করুন
- Conclusion যোগ করুন
- Keyword stuffing করবেন না
- Reader friendly করুন

IMPORTANT:

TITLE:
SEARCH_DESCRIPTION:
LABELS:

এই format পরিবর্তন করবেন না।

CONTENT: এর পরে শুধু article লিখবেন।

"""

    last_error = None

    for model in MODELS:

        for attempt in range(MAX_RETRY):

            try:

                print(
                    f"Trying model: {model} | "
                    f"Attempt {attempt + 1}/{MAX_RETRY}"
                )

                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                if response.text:

                    print(
                        "✅ Article generated successfully"
                    )

                    return response.text

                else:

                    print(
                        "⚠️ Gemini returned empty response."
                    )

                    last_error = Exception(
                        "Gemini returned empty response."
                    )

                    wait_time = 10

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

            except Exception as e:

                last_error = e

                error_text = str(e)

                print(
                    "Gemini Error:",
                    error_text
                )

                # 429 / API quota / rate limit
                if (
                    "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    wait_time = min(
                        30 * (attempt + 1),
                        120
                    )

                    print(
                        "⚠️ Gemini quota or rate limit."
                    )

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue

                # Temporary Gemini / Google server problems
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "500" in error_text
                    or "502" in error_text
                    or "504" in error_text
                ):

                    wait_time = min(
                        10 * (2 ** attempt),
                        90
                    )

                    print(
                        "⚠️ Gemini temporarily unavailable."
                    )

                    print(
                        f"Retrying in {wait_time} seconds..."
                    )

                    time.sleep(wait_time)

                    continue

                # Model not found
                if (
                    "404" in error_text
                    or "NOT_FOUND" in error_text
                ):

                    print(
                        f"❌ Model unavailable: {model}"
                    )

                    break

                # Authentication error
                if (
                    "401" in error_text
                    or "UNAUTHENTICATED" in error_text
                    or "API_KEY_INVALID" in error_text
                ):

                    raise Exception(
                        "Gemini API authentication failed. "
                        "Check GEMINI_API_KEY."
                    )

                # Permission error
                if (
                    "403" in error_text
                    or "PERMISSION_DENIED" in error_text
                ):

                    raise Exception(
                        "Gemini API permission denied. "
                        "Check API key and project settings."
                    )

                # Other unexpected errors
                wait_time = 10

                print(
                    "⚠️ Unexpected Gemini error."
                )

                print(
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

    raise Exception(
        "Gemini generation failed after all retries: "
        + str(last_error)
    )