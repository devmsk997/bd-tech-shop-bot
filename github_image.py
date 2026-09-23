import urllib.parse

def get_working_image_url(raw_image_url):
    """BDStall এর হটলিংক বাইপাস করে ইমেজ প্রস্তুত করা"""
    if not raw_image_url:
        return ""
        
    if raw_image_url.startswith('//'):
        raw_image_url = 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        raw_image_url = raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')
        
    encoded_url = urllib.parse.quote(raw_image_url, safe='')
    return f"https://wsrv.nl/?url={encoded_url}&output=jpg&n=-1"
