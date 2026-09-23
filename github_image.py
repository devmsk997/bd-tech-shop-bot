import requests
import base64

IMGBB_API_KEY = "8c7ec16bd83bd8fb06aa6e2b904eb120"  # ফ্রি পাবলিক API Key

def get_working_image_url(raw_image_url):
    """BDStall এর হটলিংক ব্লক বাইপাস করতে ImgBB এ আপলোড করে ডাইরেক্ট লিঙ্ক তৈরি"""
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
        # BDStall থেকে ছবি ডাউনলোড
        headers = {'User-Agent': 'Mozilla/5.0'}
        img_response = requests.get(raw_image_url, headers=headers, timeout=15)
        
        if img_response.status_code == 200:
            # Base64 এ কনভার্ট
            base64_image = base64.b64encode(img_response.content).decode('utf-8')
            
            # ImgBB তে আপলোড
            payload = {
                "key": IMGBB_API_KEY,
                "image": base64_image
            }
            res = requests.post("https://api.imgbb.com/1/upload", data=payload, timeout=20)
            res_json = res.json()
            
            if res.status_code == 200 and res_json.get("success"):
                direct_url = res_json['data']['url']
                print(f"🖼️ ImgBB Host Success: {direct_url}")
                return direct_url
    except Exception as e:
        print(f"⚠️ ImgBB Upload Exception: {e}")

    return raw_image_url
