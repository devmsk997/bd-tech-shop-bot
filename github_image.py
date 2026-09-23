import requests

def get_working_image_url(raw_image_url):
    """BDStall image handler with robust real-world fallback"""
    if not raw_image_url:
        return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=60"
        
    raw_image_url = raw_image_url.strip()
    if raw_image_url.startswith('//'):
        raw_image_url = 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        raw_image_url = raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')

    try:
        # Telegra.ph এ আপলোড করার চেষ্টা
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://www.bdstall.com/'
        }
        res = requests.get(raw_image_url, headers=headers, timeout=15)
        
        if res.status_code == 200 and len(res.content) > 500:
            files = {'file': ('image.jpg', res.content, 'image/jpeg')}
            up_res = requests.post('https://telegra.ph/upload', files=files, timeout=15)
            if up_res.status_code == 200:
                data = up_res.json()
                if isinstance(data, list) and len(data) > 0 and 'src' in data[0]:
                    success_url = 'https://telegra.ph' + data[0]['src']
                    print(f"✅ Telegra.ph Success: {success_url}")
                    return success_url
    except Exception as e:
        print(f"⚠️ Error: {e}")

    # যদি BDStall ব্লক করে দেয়, তবে একটি গ্যারান্টিড সচল হাই-কোয়ালিটি গ্যাজেট ইমেজ ব্যাকআপ হিসেবে দেখাবে যা ব্লগারে কখনোই ভাঙবে না
    print("⚠️ Using guaranteed working tech fallback image...")
    return "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop&q=60"
