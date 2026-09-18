#!/usr/bin/env python3
import os
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Base directory (document root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_all_html_files():
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def resolve_path(base_dir, file_path, link_href):
    """
    Resolve a link href relative to the file's path, then check if it exists under base_dir.
    This mimics how browsers resolve links.
    """
    # Get the directory containing the file
    file_dir = os.path.dirname(file_path)
    
    # Resolve the link relative to the file's directory
    # This handles ../ and ./ correctly
    absolute_link_path = os.path.normpath(os.path.join(file_dir, link_href))
    
    # Now check if this path exists under the base_dir
    # If the resolved path is already under base_dir, use it as-is
    # If it's outside, we still check it (for cases like linking outside the site)
    return absolute_link_path

def check_file(filepath):
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    
    # Check title
    if not soup.title or not soup.title.string.strip():
        issues.append("Missing or empty title tag")
    
    # Check meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if not meta_desc or not meta_desc.get('content', '').strip():
        issues.append("Missing or empty meta description")
    
    # Check images
    for img in soup.find_all('img'):
        src = img.get('src')
        if not src:
            issues.append("Image missing src attribute")
            continue
        # Skip data URIs and absolute URLs
        if src.startswith('data:') or src.startswith('http://') or src.startswith('https://'):
            continue
        # Resolve relative to the document root (BASE_DIR)
        img_path = os.path.join(BASE_DIR, src.lstrip('/') if src.startswith('/') else src)
        # If the src was relative to the file, we need to resolve it relative to the file first
        if not os.path.isabs(src) and not src.startswith('../') and not src.startswith('./'):
            # It's a relative path like "image.jpg" or "path/image.jpg"
            # Resolve relative to the file's directory first
            file_dir = os.path.dirname(filepath)
            img_path = os.path.normpath(os.path.join(file_dir, src))
        # Now check if the resolved path exists
        if not os.path.exists(img_path):
            issues.append(f"Image not found: {src}")
        # Check alt attribute
        if not img.get('alt'):
            issues.append(f"Image missing alt attribute: {src}")
    
    # Check internal links (to other HTML files)
    seen_links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Skip empty, anchor-only, mailto, tel, external http links
        if not href or href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('http://') or href.startswith('https://'):
            continue
        # Split off anchor part
        if '#' in href:
            href_part = href.split('#')[0]
            # If href_part is empty, it's a pure anchor link on the same page -> skip
            if not href_part:
                continue
        else:
            href_part = href
        # Avoid duplicate reporting of the same link in this file
        if href_part in seen_links:
            continue
        seen_links.add(href_part)
        
        # Resolve the link properly
        try:
            link_path = resolve_path(BASE_DIR, filepath, href_part)
            # If it's a directory, assume index.html
            if os.path.isdir(link_path):
                link_path = os.path.join(link_path, 'index.html')
            # If it doesn't have .html extension, we might want to check if adding .html helps
            # But for now, we'll check as is
            if not os.path.exists(link_path):
                # Try adding .html if the href didn't have it and it's not already a file
                if not href_part.endswith('.html') and not os.path.isdir(link_path):
                    link_path_html = link_path + '.html'
                    if os.path.exists(link_path_html):
                        continue  # Found it with .html added
                issues.append(f"Link not found: {href}")
        except Exception as e:
            issues.append(f"Error resolving link {href}: {e}")
    
    # Check for schema.org JSON-LD
    json_ld = soup.find_all('script', type='application/ld+json')
    if not json_ld:
        issues.append("No JSON-LD schema markup found")
    else:
        for script in json_ld:
            if not script.string.strip():
                issues.append("Empty JSON-LD script tag")
    
    return issues

def main():
    html_files = get_all_html_files()
    if not html_files:
        print("No HTML files found.")
        return
    
    total_issues = 0
    for filepath in html_files:
        rel_path = os.path.relpath(filepath, BASE_DIR)
        issues = check_file(filepath)
        if issues:
            print(f"\n{rel_path}:")
            for issue in issues:
                print(f"  - {issue}")
            total_issues += len(issues)
        else:
            print(f"\n{rel_path}: No issues found.")
    
    print(f"\nTotal issues found: {total_issues}")

if __name__ == '__main__':
    main()