import requests
import base64

def get_working_image_url(raw_image_url):
    """BDStall এর পিকচার ডাউনলোড করে ImgBB এর মাধ্যমে স্থায়ী ইমেজে রূপান্তর"""
    if not raw_image_url:
        return ""
        
    raw_image_url = raw_image_url.strip()
    if raw_image_url.startswith('//'):
        raw_image_url = 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        raw_image_url = raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')

    # ১. BDStall থেকে ছবি ডাউনলোড
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.bdstall.com/'
        }
        response = requests.get(raw_image_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            base64_image = base64.b64encode(response.content).decode('utf-8')
            
            # ২. ImgBB তে আপলোড (Multiple Key for safety)
            api_keys = ["8c7ec16bd83bd8fb06aa6e2b904eb120", "3d29486c7526bfd2e7d7045dfefbd1e6"]
            for key in api_keys:
                try:
                    res = requests.post(
                        "https://api.imgbb.com/1/upload",
                        data={"key": key, "image": base64_image},
                        timeout=15
                    )
                    res_data = res.json()
                    if res.status_code == 200 and res_data.get("success"):
                        final_url = res_data['data']['url']
                        print(f"🖼️ ImgBB Upload Success: {final_url}")
                        return final_url
                except Exception:
                    continue
    except Exception as e:
        print(f"⚠️ Image Download Error: {e}")

    # Fallback to direct raw image
    return raw_image_url
