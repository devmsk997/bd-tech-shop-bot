import requests
import base64

def get_working_image_url(raw_image_url):
    """BDStall hotlink blockage permanent fix via Base64/Free Hosting"""
    if not raw_image_url:
        return ""
        
    raw_image_url = raw_image_url.strip()
    if raw_image_url.startswith('//'):
        raw_image_url = 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        raw_image_url = raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')

    # জেনুইন ব্রাউজার সেজে ছবি ডাউনলোড (Bypass BDStall Protection)
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bdstall.com/'
        }
        res = requests.get(raw_image_url, headers=headers, timeout=15)
        
        if res.status_code == 200:
            # Base64 এ কনভার্ট
            b64_data = base64.b64encode(res.content).decode('utf-8')
            
            # PostImages / ImgBB External Hosting Upload
            upload_res = requests.post(
                "https://api.imgbb.com/1/upload",
                data={
                    "key": "8c7ec16bd83bd8fb06aa6e2b904eb120", 
                    "image": b64_data
                },
                timeout=20
            )
            up_json = upload_res.json()
            if upload_res.status_code == 200 and up_json.get("success"):
                direct_url = up_json['data']['url']
                print(f"🖼️ Permanent Image Hosted: {direct_url}")
                return direct_url
                
            # হোস্টিং ফেইল করলে সরাসরি Data URI রিটার্ন করবে (যা কখনো ভাঙবে না)
            print("⚠️ Hosting failed, using embedded Base64 Data URI...")
            return f"data:image/jpeg;base64,{b64_data}"
            
    except Exception as e:
        print(f"⚠️ Image Download Exception: {e}")

    return raw_image_url
