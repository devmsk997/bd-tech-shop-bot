import requests

def get_working_image_url(raw_image_url, title=""):
    """BDStall image handler with smart category-based matching fallback"""
    if raw_image_url:
        try:
            raw_image_url = raw_image_url.strip()
            if raw_image_url.startswith('//'):
                raw_image_url = 'https:' + raw_image_url
            elif raw_image_url.startswith('http://'):
                raw_image_url = raw_image_url.replace('http://', 'https://')
            elif not raw_image_url.startswith('http'):
                raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Referer': 'https://www.bdstall.com/'
            }
            res = requests.get(raw_image_url, headers=headers, timeout=10)
            if res.status_code == 200 and len(res.content) > 500:
                files = {'file': ('image.jpg', res.content, 'image/jpeg')}
                up_res = requests.post('https://telegra.ph/upload', files=files, timeout=10)
                if up_res.status_code == 200:
                    data = up_res.json()
                    if isinstance(data, list) and len(data) > 0 and 'src' in data[0]:
                        return 'https://telegra.ph' + data[0]['src']
        except Exception:
            pass

    # প্রোডাক্টের নাম দেখে স্বয়ংক্রিয়ভাবে সঠিক ক্যাটাগরির ছবি সিলেক্ট করার স্মার্ট ফলব্যাক
    title_lower = title.lower()
    if 'phone' in title_lower or 'iphone' in title_lower or 'mobile' in title_lower:
        return "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&auto=format&fit=crop&q=60"
    elif 'laptop' in title_lower or 'computer' in title_lower or 'mackbook' in title_lower:
        return "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&auto=format&fit=crop&q=60"
    elif 'watch' in title_lower:
        return "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&auto=format&fit=crop&q=60"
    elif 'earbud' in title_lower or 'headphone' in title_lower or 'sound' in title_lower:
        return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=60"
    elif 'camera' in title_lower or 'cctv' in title_lower:
        return "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800&auto=format&fit=crop&q=60"
    else:
        return "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=800&auto=format&fit=crop&q=60"
