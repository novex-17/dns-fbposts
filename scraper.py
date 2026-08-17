import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

DEFAULT_CATEGORIES = [
    {"name": "Iron Set (ชุดเหล็ก)", "url": "https://dnsgolfoutlet.com/product-category/iron-set", "tag": "#IronSet #ชุดเหล็ก"},
    {"name": "Driver (ไม้ 1)", "url": "https://dnsgolfoutlet.com/product-category/driver", "tag": "#Driver"},
    {"name": "Fairway (แฟร์เวย์)", "url": "https://dnsgolfoutlet.com/product-category/fairway", "tag": "#Fairway #fairwaywood"},
    {"name": "Hybrid / Utility (ไฮบริด)", "url": "https://dnsgolfoutlet.com/product-category/hybrid-utilities", "tag": "#Hybrid #Utility"},
    {"name": "Wedge (เวดจ์)", "url": "https://dnsgolfoutlet.com/product-category/wedges", "tag": "#Wedge"},
    {"name": "Putter (พัตเตอร์)", "url": "https://dnsgolfoutlet.com/product-category/putters", "tag": "#Putter"},
    {"name": "New Arrivals (สินค้ามาใหม่ทั้งหมด)", "url": "https://dnsgolfoutlet.com/product-category/new-arrivals", "tag": "#NewArrivals #สินค้ามาใหม่"},
    {"name": "Lady (ไม้ผู้หญิง)", "url": "https://dnsgolfoutlet.com/product-category/lady", "tag": "#LadyGolf"},
    {"name": "Lefty (ไม้มือซ้าย)", "url": "https://dnsgolfoutlet.com/product-category/lefty", "tag": "#LeftyGolf"}
]

URL_MAPPINGS = {
    "/putter": "/putters",
    "/wedge": "/wedges",
    "/utility-hybrid": "/hybrid-utilities",
    "/hybrid": "/hybrid-utilities"
}

def clean_url(url):
    if not url:
        return ""
    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        url = "https://dnsgolfoutlet.com" + url
        
    # Auto-correct singular URLs to official DNS Golf Outlet URLs
    for wrong_path, right_path in URL_MAPPINGS.items():
        if url.endswith(wrong_path) or (wrong_path + "/") in url:
            url = url.replace(wrong_path, right_path)
            
    return url

def fetch_product_detail(product_info):
    product_url = product_info['url']
    try:
        res = requests.get(product_url, headers=HEADERS, timeout=12)
        if res.status_code != 200:
            return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 1. Extract Description
        description = ""
        tab_desc = soup.find('div', id='tab-description')
        if not tab_desc:
            tab_desc = soup.find('div', class_=re.compile(r'woocommerce-Tabs-panel--description'))
        
        if tab_desc:
            lines = []
            elements = tab_desc.find_all(['p', 'div', 'li'])
            for el in elements:
                if not el.find_all(['p', 'div']):
                    txt = el.get_text(strip=True)
                    if txt and (not lines or lines[-1] != txt):
                        lines.append(txt)
            
            if not lines:
                raw_text = tab_desc.get_text("\n", strip=True)
                for line in raw_text.split("\n"):
                    line = line.strip()
                    if line and (not lines or lines[-1] != line):
                        lines.append(line)
            
            description = "\n".join(lines)
        else:
            short_desc = soup.find('div', class_=re.compile(r'short-description|entry-summary'))
            if short_desc:
                description = short_desc.get_text("\n", strip=True)

        # 2. Extract First Image
        first_img_url = ""
        gallery_item = soup.find('div', class_=re.compile(r'woocommerce-product-gallery__image'))
        if gallery_item:
            a_tag = gallery_item.find('a')
            if a_tag and a_tag.get('href'):
                first_img_url = a_tag.get('href')
            else:
                img_tag = gallery_item.find('img')
                if img_tag:
                    first_img_url = img_tag.get('data-large_image') or img_tag.get('data-src') or img_tag.get('src')
        
        if not first_img_url:
            post_img = soup.find('img', class_=re.compile(r'wp-post-image'))
            if post_img:
                first_img_url = post_img.get('data-large_image') or post_img.get('data-src') or post_img.get('src')

        first_img_url = clean_url(first_img_url)

        return {
            'url': product_url,
            'title': product_info.get('title', ''),
            'is_new': product_info.get('is_new', False),
            'description': description.strip(),
            'image_url': first_img_url
        }
    except Exception as e:
        print(f"Error fetching product detail {product_url}: {e}")
        return None

def fetch_category_items(category_url, filter_mode="all"):
    category_url = clean_url(category_url)
    res = requests.get(category_url, headers=HEADERS, timeout=15)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch category page. Status code: {res.status_code}")
    
    soup = BeautifulSoup(res.text, 'html.parser')
    product_divs = soup.find_all('div', class_=re.compile(r'product-small|type-product'))
    
    available_items = []
    
    for p_div in product_divs:
        classes = p_div.get('class', [])
        class_str = " ".join(classes)
        
        # Skip if out of stock
        if 'out-of-stock' in class_str or 'outofstock' in class_str:
            continue
        
        price_badge = p_div.find('div', class_=re.compile(r'price|badge'))
        if price_badge and 'SOLD OUT' in price_badge.get_text().upper():
            continue

        link_tag = p_div.find('a', href=re.compile(r'/product/'))
        if not link_tag:
            continue
            
        prod_url = clean_url(link_tag.get('href'))
        title = link_tag.get('aria-label') or link_tag.get_text(strip=True)
        
        # Check if product is NEW arrival
        badge_div = p_div.find('div', class_=re.compile(r'badge'))
        badge_text = badge_div.get_text(strip=True).upper() if badge_div else ''
        
        is_new = ('NEW' in badge_text) or ('product_cat-new-arrivals' in class_str) or bool(p_div.find(class_=re.compile(r'new-bubble-auto')))
        
        # If user selected filter_mode == "new_only", skip non-new items
        if filter_mode == "new_only" and not is_new:
            continue
        
        if not any(item['url'] == prod_url for item in available_items):
            available_items.append({
                'title': title,
                'url': prod_url,
                'is_new': is_new
            })
            
    print(f"Found {len(available_items)} matching items (filter_mode={filter_mode}) for URL: {category_url}")
    
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(fetch_product_detail, item) for item in available_items]
        for f in futures:
            res_detail = f.result()
            if res_detail and res_detail['description']:
                results.append(res_detail)
                
    return results

def get_default_caption(category_url="https://dnsgolfoutlet.com/product-category/driver", category_tag="#Driver", filter_mode="all"):
    today_str = datetime.now().strftime("%d/%m/%Y")
    
    header_title = f"#รวม {category_tag} มือสอง ของดีใช้ยาวๆ"
    if filter_mode == "new_only":
        header_title = f"🔥#อัพเดทใหม่ล่าสุด #สินค้ามาใหม่ {category_tag} มือสอง สภาพสวยๆ"
        
    return f"""{header_title}
นำเข้าจากญี่ปุ่น {today_str} อัพเดทสินค้าได้แล้วที่ : {category_url}
รายละเอียดอยู่ใต้ภาพทุกรูป เลื่อนคลิกเข้าชมเพิ่มเติมได้ตามลิงค์
.
📥 ค่าส่ง 100/150 บาท 
.
🛒 ช่องทางสั่งซื้อ INBOX
💳 รับบัตรเครดิต
📄 ออกใบกำกับภาษีได้
.
☎️ นิว 090-951-6412
☎️ กาย 061-535-7425
. 
📍 หน้าร้าน อยู่ซอยสุขุมวิท 62 : https://maps.app.goo.gl/E3EpWrGqBb9LTHQr7
.
#Driver #Fairway #Hybrid #IronSet #Wedge #Putter #DNS #DonAndSons #ไม้กอล์ฟ #ไม้กอล์ฟนำเข้า #ไม้กอล์ฟนำเข้าจากญี่ปุ่น"""
