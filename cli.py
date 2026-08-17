#!/usr/bin/env python3
import sys
import os
import argparse
from scraper import fetch_category_items, get_default_caption, DEFAULT_CATEGORIES

def main():
    parser = argparse.ArgumentParser(description="DNS Golf Outlet Social Media Facebook Post Generator CLI")
    parser.add_argument("category", nargs="?", default="iron-set", help="Category name (iron-set, driver, fairway, utility-hybrid, wedge, putter, new-arrivals) or full URL")
    parser.add_argument("-n", "--new-only", action="store_true", help="Fetch ONLY new arrival clubs (items with (New) badge)")
    parser.add_argument("-o", "--output", help="Save output to file")
    
    args = parser.parse_args()
    
    category_input = args.category.strip().lower()
    filter_mode = "new_only" if args.new_only else "all"
    
    category_url = category_input
    category_tag = "#ไม้กอล์ฟ"
    
    for cat in DEFAULT_CATEGORIES:
        if category_input in cat['name'].lower() or category_input in cat['url'].lower():
            category_url = cat['url']
            category_tag = cat['tag']
            break
            
    if not category_url.startswith("http"):
        category_url = f"https://dnsgolfoutlet.com/product-category/{category_input}"
        
    mode_text = "✨ NEW ARRIVALS ONLY" if args.new_only else "ALL IN-STOCK"
    print(f"⛳ Scraping {mode_text} items from: {category_url}")
    
    try:
        items = fetch_category_items(category_url, filter_mode=filter_mode)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
        
    if not items:
        print("⚠️ No matching in-stock items found on this page.")
        sys.exit(0)
        
    main_caption = get_default_caption(category_url, category_tag, filter_mode=filter_mode)
    
    output_text = []
    output_text.append("==================================================")
    output_text.append(f"📌 MAIN FACEBOOK POST CAPTION ({mode_text})")
    output_text.append("==================================================")
    output_text.append(main_caption)
    output_text.append("\n" + "="*50)
    output_text.append(f"🖼️ ITEM PHOTO CAPTIONS ({len(items)} Items)")
    output_text.append("="*50 + "\n")
    
    for idx, item in enumerate(items, 1):
        badge = " [✨ NEW]" if item.get('is_new') else ""
        output_text.append(f"--- PHOTO #{idx}{badge} ---")
        output_text.append(f"📷 Image: {item['image_url']}")
        output_text.append(f"📝 Caption:\n{item['description']}")
        output_text.append(f"{item['url']}\n")
        
    final_output = "\n".join(output_text)
    
    print(final_output)
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(final_output)
        print(f"\n✅ Saved report to: {args.output}")

if __name__ == "__main__":
    main()
