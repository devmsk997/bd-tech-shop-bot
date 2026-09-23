import requests

def get_working_image_url(raw_image_url):
    """BDStall hotlink bypass and upload to Telegra.ph with robust fallback"""
    if not raw_image_url:
        return "https://i.ibb.co/6Wv4Y6b/placeholder.png"
        
    raw_image_url = raw_image_url.strip()
    if raw_image_url.startswith('//'):
        raw_image_url = 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        raw_image_url = raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Referer': 'https://www.bdstall.com/'
        }
        res = requests.get(raw_image_url, headers=headers, timeout=20)
        
        if res.status_code == 200 and len(res.content) > 500:
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

    # যদি কোনো কারণে ফেইল করে, তবে সরাসরি র সুত্র না দিয়ে একটি সফল প্রক্সি লিংক ব্যাকআপ দেওয়া হলো
    print("⚠️ Using proxy fallback for image...")
    return f"https://images.weserv.nl/?url={raw_image_url}&output=jpg"
