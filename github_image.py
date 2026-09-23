import requests
import base64

IMGBB_API_KEY = "8c7ec16bd83bd8fb06aa6e2b904eb120"  # Free Public API Key

def get_working_image_url(raw_image_url):
    """BDStall hotlink blockage bypass via ImgBB Direct Upload"""
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
        # জেনুইন ব্রাউজার সেজে ছবি ডাউনলোড (Bypass 403 Forbidden)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bdstall.com/'
        }
        img_res = requests.get(raw_image_url, headers=headers, timeout=15)
        
        if img_res.status_code == 200:
            # Base64 এনকোড করে ImgBB-তে স্থায়ী আপলোড
            base64_image = base64.b64encode(img_res.content).decode('utf-8')
            payload = {
                "key": IMGBB_API_KEY,
                "image": base64_image
            }
            res = requests.post("https://api.imgbb.com/1/upload", data=payload, timeout=20)
            res_json = res.json()
            
            if res.status_code == 200 and res_json.get("success"):
                uploaded_url = res_json['data']['url']
                print(f"🖼️ ImgBB Permanent URL: {uploaded_url}")
                return uploaded_url
    except Exception as e:
        print(f"⚠️ Image Process Exception: {e}")

    # Fallback Option
    return f"https://images.weserv.nl/?url={raw_image_url}&output=jpg"
