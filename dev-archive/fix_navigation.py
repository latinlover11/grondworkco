#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_all_html_files():
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def fix_navigation_links():
    """Fix navigation links to be root-relative so they work from any page"""
    html_files = get_all_html_files()
    fixed_count = 0
    
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        modified = False
        
        # Find all navigation links in header
        # Desktop navigation links
        for link in soup.select('header .nav-links a[href]'):
            href = link['href']
            # Fix links to make them root-relative
            if href == 'index.html#services':
                link['href'] = '/#services'
                modified = True
                print(f"Fixed link in {os.path.relpath(filepath, BASE_DIR)}: index.html#services -> /#services")
            elif href == 'index.html#process':
                link['href'] = '/#process'
                modified = True
                print(f"Fixed link in {os.path.relpath(filepath, BASE_DIR)}: index.html#process -> /#process")
            elif href == 'work.html':
                link['href'] = '/work.html'
                modified = True
                print(f"Fixed link in {os.path.relpath(filepath, BASE_DIR)}: work.html -> /work.html")
            elif href == 'about.html':
                link['href'] = '/about.html'
                modified = True
                print(f"Fixed link in {os.path.relpath(filepath, BASE_DIR)}: about.html -> /about.html")
            elif href == 'contact.html':
                link['href'] = '/contact.html'
                modified = True
                print(f"Fixed link in {os.path.relpath(filepath, BASE_DIR)}: contact.html -> /contact.html")
        
        # Mobile navigation links (same as desktop)
        for link in soup.select('.nav-mobile-panel a[href]'):
            href = link['href']
            # Fix links to make them root-relative
            if href == 'index.html#services':
                link['href'] = '/#services'
                modified = True
                print(f"Fixed mobile link in {os.path.relpath(filepath, BASE_DIR)}: index.html#services -> /#services")
            elif href == 'index.html#process':
                link['href'] = '/#process'
                modified = True
                print(f"Fixed mobile link in {os.path.relpath(filepath, BASE_DIR)}: index.html#process -> /#process")
            elif href == 'work.html':
                link['href'] = '/work.html'
                modified = True
                print(f"Fixed mobile link in {os.path.relpath(filepath, BASE_DIR)}: work.html -> /work.html")
            elif href == 'about.html':
                link['href'] = '/about.html'
                modified = True
                print(f"Fixed mobile link in {os.path.relpath(filepath, BASE_DIR)}: about.html -> /about.html")
            elif href == 'contact.html':
                link['href'] = '/contact.html'
                modified = True
                print(f"Fixed mobile link in {os.path.relpath(filepath, BASE_DIR)}: contact.html -> /contact.html")
        
        # Fix the CTA button (Get a quote)
        for link in soup.select('header .nav-cta[href]'):
            href = link['href']
            if href == 'contact.html':
                link['href'] = '/contact.html'
                modified = True
                print(f"Fixed CTA link in {os.path.relpath(filepath, BASE_DIR)}: contact.html -> /contact.html")
        
        # Fix sticky contact button in footer
        for link in soup.select('.sticky-contact a[href]'):
            href = link['href']
            if href == 'contact.html':
                link['href'] = '/contact.html'
                modified = True
                print(f"Fixed sticky contact link in {os.path.relpath(filepath, BASE_DIR)}: contact.html -> /contact.html")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            fixed_count += 1
    
    print(f"\nFixed navigation links in {fixed_count} files.")

def main():
    print("Fixing navigation links to be root-relative...")
    fix_navigation_links()
    print("Done!")

if __name__ == '__main__':
    main()