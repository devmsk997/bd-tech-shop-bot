import requests
import urllib.parse
import random

def get_style(title):
    title_lower = title.lower()

    if any(word in title_lower for word in [
        "ransomware",
        "malware",
        "phishing",
        "security",
        "password",
        "vpn",
        "data breach",
        "cyber"
    ]):
        return """
Cybersecurity theme,
dark digital environment,
encrypted data,
security lock,
network protection,
hacker threat visualization,
blue and red neon lighting,
realistic 3D technology style
"""

    elif any(word in title_lower for word in [
        "ai",
        "artificial intelligence",
        "chatgpt",
        "machine learning"
    ]):
        return """
Artificial intelligence theme,
futuristic AI brain,
neural network,
digital hologram,
advanced technology interface,
blue futuristic lighting,
realistic 3D render style
"""

    elif any(word in title_lower for word in [
        "phone",
        "smartphone",
        "android",
        "mobile"
    ]):
        return """
Modern smartphone technology,
premium mobile device,
digital interface,
performance optimization concept,
clean futuristic background,
realistic product photography style
"""

    elif any(word in title_lower for word in [
        "app",
        "application"
    ]):
        return """
Mobile application technology,
modern app interface,
smartphone screen,
digital ecosystem,
clean professional technology design,
realistic 3D style
"""

    else:
        return """
Modern technology concept,
digital world,
future technology,
computer interface,
clean premium tech magazine style,
realistic 3D render
"""

def generate_image(title):
    style = get_style(title)

    prompt = f"""
Professional technology blog featured image.
Article topic: {title}
Visual style: {style}
Requirements: Premium technology magazine quality, Realistic, High detail, Professional lighting, Suitable for Blogger featured image, 16:9 aspect ratio, No text, No logo, No watermark
"""

    encoded_prompt = urllib.parse.quote(prompt.strip())
    seed = random.randint(1000, 999999)

    # nologo=true যুক্ত করা হয়েছে যাতে ছবি একদম পরিষ্কার ও লোগো মুক্ত আসে
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?seed={seed}&nologo=true"
    filename = "featured_image.jpg"

    try:
        response = requests.get(url, timeout=120)

        if response.status_code == 200:
            with open(filename, "wb") as file:
                file.write(response.content)

            print(f"✅ Image prepared for Blogger: {filename}")
            return filename

        else:
            print(f"⚠️ Image generation failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"⚠️ Image error: {e}")
        return None
