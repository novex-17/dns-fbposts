from flask import Flask, render_template, request, jsonify, send_file
import io
import os
import re
import requests
import zipfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from scraper import fetch_category_items, get_default_caption, DEFAULT_CATEGORIES, HEADERS

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    return send_file(os.path.join(app.root_path, 'static', 'index.html'))

@app.route('/api/categories', methods=['GET'])
def api_categories():
    return jsonify(DEFAULT_CATEGORIES)

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    data = request.json or {}
    category_url = data.get('category_url', 'https://dnsgolfoutlet.com/product-category/driver').strip()
    filter_mode = data.get('filter_mode', 'all').strip()  # 'all' or 'new_only'
    
    # Find matching tag if preset
    category_tag = "#ไม้กอล์ฟ"
    for cat in DEFAULT_CATEGORIES:
        if cat['url'].rstrip('/') in category_url.rstrip('/'):
            category_tag = cat['tag']
            break
            
    try:
        items = fetch_category_items(category_url, filter_mode=filter_mode)
        main_caption = get_default_caption(category_url, category_tag, filter_mode=filter_mode)
        return jsonify({
            'success': True,
            'count': len(items),
            'filter_mode': filter_mode,
            'main_caption': main_caption,
            'items': items
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def download_single_image(img_url):
    try:
        res = requests.get(img_url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            return res.content
    except Exception as e:
        print(f"Error downloading image {img_url}: {e}")
    return None

@app.route('/api/download-zip', methods=['POST'])
def api_download_zip():
    data = request.json or {}
    main_caption = data.get('main_caption', '')
    items = data.get('items', [])
    filter_mode = data.get('filter_mode', 'all')
    
    if not items:
        return jsonify({'error': 'No items provided'}), 400

    zip_buffer = io.BytesIO()
    
    image_futures = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for idx, item in enumerate(items, 1):
            img_url = item.get('image_url', '')
            image_futures.append((idx, item, executor.submit(download_single_image, img_url)))
            
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("00_MAIN_CAPTION.txt", main_caption.encode('utf-8'))
        
        all_combined_captions = [f"=== MAIN POST CAPTION ===\n\n{main_caption}\n\n" + "="*50 + "\n\n"]

        for idx, item, future in image_futures:
            img_bytes = future.result()
            photo_caption = f"{item.get('description', '').strip()}\n{item.get('url', '')}"
            
            clean_title = re.sub(r'[^\w\s-]', '', item.get('description', '').split('\n')[0])[:30].strip() or f"item_{idx}"
            is_new_tag = "_NEW" if item.get('is_new') else ""
            img_filename = f"{idx:02d}{is_new_tag}_{clean_title}.jpg"
            caption_filename = f"{idx:02d}{is_new_tag}_{clean_title}_caption.txt"
            
            if img_bytes:
                zf.writestr(f"images/{img_filename}", img_bytes)
            
            zf.writestr(f"captions/{caption_filename}", photo_caption.encode('utf-8'))
            
            badge_str = " [✨ NEW]" if item.get('is_new') else ""
            all_combined_captions.append(f"--- PHOTO #{idx}{badge_str}: {img_filename} ---\n{photo_caption}\n\n")

        zf.writestr("ALL_PHOTO_CAPTIONS_COMBINED.txt", "".join(all_combined_captions).encode('utf-8'))

    zip_buffer.seek(0)
    mode_tag = "new_clubs_" if filter_mode == "new_only" else ""
    filename = f"dns_golf_fb_{mode_tag}{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5050))
    print(f"Starting DNS Golf Social Media Assistant Server on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
