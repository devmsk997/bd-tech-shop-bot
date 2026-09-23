def get_working_image_url(raw_image_url):
    """BDStall এর সরাসরি সঠিক ইমেজ লিঙ্ক প্রস্তুত করা"""
    if not raw_image_url:
        return ""
        
    raw_image_url = raw_image_url.strip()
    
    # ইউআরএল ফরম্যাট সঠিকভাবে ঠিক করা
    if raw_image_url.startswith('//'):
        return 'https:' + raw_image_url
    elif raw_image_url.startswith('http://'):
        return raw_image_url.replace('http://', 'https://')
    elif not raw_image_url.startswith('http'):
        return 'https://www.bdstall.com/' + raw_image_url.lstrip('/')
        
    return raw_image_url
