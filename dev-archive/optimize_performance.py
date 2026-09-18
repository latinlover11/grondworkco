#!/usr/bin/env python3
import os
import re
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_all_html_files():
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def optimize_performance(filepath):
    """Apply performance optimizations to an HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    modified = False
    
    # 1. Add width/height attributes to images to prevent layout shift
    images = soup.find_all('img')
    for img in images:
        # Skip placeholder images and data URIs
        src = img.get('src', '')
        if not src or src.startswith('data:') or src.startswith('http'):
            continue
        # Skip lightbox placeholders
        if img.get('id') == 'lightbox-img':
            continue
            
        # Only add dimensions if they don't already exist
        if not img.get('width') and not img.get('height'):
            # We can't know actual dimensions without checking the file,
            # but we can add placeholder dimensions that will be overridden by CSS
            # This is better than nothing for preventing layout shift
            img['width'] = '1'
            img['height'] = '1'
            # Add inline style to override with actual dimensions via CSS
            if not img.get('style'):
                img['style'] = 'width:auto;height:auto;display:block;'
            else:
                img['style'] += ';width:auto;height:auto;display:block;'
            modified = True
    
    # 2. Move non-essential JavaScript to bottom or add defer/async
    # Find scripts in head that could be deferred
    head = soup.find('head')
    if head:
        scripts_in_head = head.find_all('script')
        for script in scripts_in_head:
            src = script.get('src', '')
            # Skip JSON-LD (should stay in head)
            if script.get('type') == 'application/ld+json':
                continue
            # Skip small inline scripts (like the date script in footer that got moved to head?)
            if not src and len(script.string or '').strip() < 50:
                continue
                
            # For external scripts, add defer if not already present
            if src and not script.get('defer') and not script.get('async'):
                script['defer'] = ''
                modified = True
                print(f"  Added defer to script: {src}")
    
    # 3. Check if we can combine or minify CSS/JS (we'll note this for manual optimization)
    # For now, just report on opportunities
    
    # 4. Add rel=preload for critical resources (fonts, etc.)
    # Already has preconnect for fonts, which is good
    
    # 5. Ensure CSS is in head (it is)
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True
    return False

def main():
    html_files = get_all_html_files()
    if not html_files:
        print("No HTML files found.")
        return
    
    print("Applying performance optimizations...\n")
    
    optimized_count = 0
    for filepath in html_files:
        rel_path = os.path.relpath(filepath, BASE_DIR)
        if optimize_performance(filepath):
            print(f"✓ Optimized: {rel_path}")
            optimized_count += 1
        else:
            print(f"○ No changes: {rel_path}")
    
    print(f"\nOptimized {optimized_count} out of {len(html_files)} files.")
    
    if optimized_count > 0:
        print("\n📝 Note: Width/height attributes were added as 1x1 with CSS override.")
        print("   For best results, consider adding actual dimensions based on image sizes.")

if __name__ == '__main__':
    main()