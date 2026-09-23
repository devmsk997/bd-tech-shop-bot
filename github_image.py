import urllib.parse

def get_working_image_url(raw_image_url):
    """BDStall এর হটলিংক বাইপাস করে নির্ভরযোগ্য CDN ইমেজ প্রস্তুত করা"""
    if not raw_image_url:
        return ""
        
    # ইউআরএল ফরম্যাট সঠিকভাবে ঠিক করা
    raw_image_url = raw_image_url.strip()
    if raw_image_url.startswith('//'):
        raw_image_url = 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        raw_image_url = raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')
        
    #wsrv.nl CDN দিয়ে এনকোডেড ইমেজ রিটার্ন
    encoded_url = urllib.parse.quote(raw_image_url, safe='')
    return f"https://wsrv.nl/?url={encoded_url}&output=jpg&n=-1"
