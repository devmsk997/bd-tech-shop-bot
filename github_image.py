import requests
import base64

def get_working_image_url(raw_image_url):
    """BDStall Protection Bypass and Convert to Permanent CDN Image"""
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
        # Real Chrome Browser Session to Download Image
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
            'Referer': 'https://www.bdstall.com/'
        }
        
        response = session.get(raw_image_url, headers=headers, timeout=20)
        
        if response.status_code == 200 and len(response.content) > 1000:
            b64_image = base64.b64encode(response.content).decode('utf-8')
            
            # ImgBB Upload
            imgbb_url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": "8c7ec16bd83bd8fb06aa6e2b904eb120",
                "image": b64_image
            }
            res = requests.post(imgbb_url, data=payload, timeout=20)
            res_json = res.json()
            
            if res.status_code == 200 and res_json.get("success"):
                hosted_url = res_json['data']['url']
                print(f"✅ ImgBB Hosted Success: {hosted_url}")
                return hosted_url
            
            # Fallback: Embedded Base64 Image string
            print("⚠️ ImgBB Upload Failed, Using Base64 Fallback")
            return f"data:image/jpeg;base64,{b64_image}"
            
    except Exception as e:
        print(f"❌ Image Processing Error: {e}")

    return raw_image_url
