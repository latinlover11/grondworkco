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

def remove_process_contact_from_nav():
    """Remove Process and Contact from navigation links in all HTML files"""
    html_files = get_all_html_files()
    modified_count = 0
    
    for filepath in html_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        modified = False
        
        # Find and remove Process and Contact from desktop navigation
        # Desktop navigation links
        for link in soup.select('header .nav-links a[href]'):
            href = link['href']
            # Check if this is a Process or Contact link
            if href in ['/#process', '/#process', 'index.html#process', 'process.html', '/process.html'] or \
               href in ['/contact.html', 'contact.html', '/contact', 'contact']:
                # Remove the entire list item
                parent_li = link.find_parent('li')
                if parent_li:
                    parent_li.decompose()
                    modified = True
                    print(f"Removed {href} from nav in {os.path.relpath(filepath, BASE_DIR)}")
        
        # Find and remove Process and Contact from mobile navigation
        for link in soup.select('.nav-mobile-panel a[href]'):
            href = link['href']
            # Check if this is a Process or Contact link
            if href in ['/#process', '/#process', 'index.html#process', 'process.html', '/process.html'] or \
               href in ['/contact.html', 'contact.html', '/contact', 'contact']:
                # Remove the entire element
                link.decompose()
                modified = True
                print(f"Removed {href} from mobile nav in {os.path.relpath(filepath, BASE_DIR)}")
        
        # Also remove CTA button if it's just "Get a quote" and we want to keep only one
        # But let's keep the CTA button for now as requested
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))
            modified_count += 1
    
    print(f"\nModified navigation in {modified_count} files.")

def main():
    print("Removing Process and Contact from navigation...")
    remove_process_contact_from_nav()
    print("Done!")

if __name__ == '__main__':
    main()