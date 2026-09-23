import requests

def get_working_image_url(raw_image_url):
    """BDStall hotlink bypass and upload to Telegra.ph Permanent CDN (No API Key needed)"""
    if not raw_image_url:
        return ""
        
    raw_image_url = raw_image_url.strip()
    if raw_image_url.startswith('//'):
        raw_image_url = 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        raw_image_url = raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')

    try:
        # ১. BDStall থেকে জেনুইন ব্রাউজার সেজে ছবি ডাউনলোড
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Referer': 'https://www.bdstall.com/'
        }
        res = requests.get(raw_image_url, headers=headers, timeout=20)
        
        if res.status_code == 200 and len(res.content) > 500:
            # ২. Telegra.ph ফ্রি সার্ভারে আপলোড (চিরস্থায়ী CDN লিঙ্ক)
            files = {'file': ('product_image.jpg', res.content, 'image/jpeg')}
            upload_res = requests.post('https://telegra.ph/upload', files=files, timeout=20)
            
            if upload_res.status_code == 200:
                data = upload_res.json()
                if isinstance(data, list) and len(data) > 0 and 'src' in data[0]:
                    permanent_url = 'https://telegra.ph' + data[0]['src']
                    print(f"✅ Telegra.ph Permanent Image URL: {permanent_url}")
                    return permanent_url
                    
    except Exception as e:
        print(f"❌ Image Upload Exception: {e}")

    return raw_image_url
