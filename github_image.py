import urllib.parse

def get_working_image_url(raw_image_url):
    """BDStall hotlink bypass with reliable image caching"""
    if not raw_image_url:
        return ""
        
    raw_image_url = raw_image_url.strip()
    
    if raw_image_url.startswith('//'):
        raw_image_url = 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        raw_image_url = raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        raw_image_url = 'https://www.bdstall.com/' + raw_image_url.lstrip('/')

    # Direct Cloudflare-backed proxy format for Blogger
    encoded_url = urllib.parse.quote(raw_image_url, safe='')
    return f"https://images.weserv.nl/?url={encoded_url}&w=800&output=jpg"
