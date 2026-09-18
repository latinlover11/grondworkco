#!/usr/bin/env python3
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def fix_blog_index_images():
    """Fix image paths in blog/index.html"""
    filepath = os.path.join(BASE_DIR, 'blog', 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Find all images in blog index
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and src.startswith('../img/case-studies/'):
            # Fix the path: blog/index.html is in blog/, need to go up two levels to reach img/
            new_src = src.replace('../img/case-studies/', '../../img/case-studies/')
            img['src'] = new_src
            print(f"Fixed image src: {src} -> {new_src}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"Updated {filepath}")

def fix_blog_post_links():
    """Fix links in blog post files that point to wrong directories"""
    blog_dir = os.path.join(BASE_DIR, 'blog')
    blog_posts = []
    
    # Get all blog post HTML files
    for file in os.listdir(blog_dir):
        if file.startswith('blog-post-') and file.endswith('.html'):
            blog_posts.append(os.path.join(blog_dir, file))
    
    for filepath in blog_posts:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        modified = False
        
        # Fix navigation links in header
        # Look for nav links that might be wrong
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Fix links that go to wrong levels
            # From blog/blog-post-X.html, we need ../ to reach root
            if href == 'index.html':
                # This would look for blog/index.html, but we want ../index.html
                link['href'] = '../index.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: index.html -> ../index.html")
            elif href == 'work.html':
                link['href'] = '../work.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: work.html -> ../work.html")
            elif href == 'about.html':
                link['href'] = '../about.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: about.html -> ../about.html")
            elif href == 'testimonials.html':
                link['href'] = '../testimonials.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: testimonials.html -> ../testimonials.html")
            elif href == 'contact.html':
                link['href'] = '../contact.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: contact.html -> ../contact.html")
            elif href == 'blog/index.html':
                # From blog/post, we need ../../blog/index.html? No, from blog/ we need blog/index.html
                # Actually from blog/blog-post-X.html, blog/ is one level up
                link['href'] = '../blog/index.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: blog/index.html -> ../blog/index.html")
        
        # Also check the article nav links (previous/next)
        # These seem to be correct already: ../blog/index.html and ../blog/blog-post-2.html
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))

def fix_blog_index_blog_links():
    """Fix links in blog/index.html that point to blog posts"""
    filepath = os.path.join(BASE_DIR, 'blog', 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    modified = False
    
    # Find blog post links (they should be like blog-post-1.html, not ./blog-post-1.html)
    for link in soup.find_all('a', href=True):
        href = link['href']
        # Links to blog posts in the same directory
        if re.match(r'blog-post-\d+\.html$', href):
            # These are already correct - they're in the same directory
            pass
        elif href == 'index.html':
            # Active link for Resources tab - this is correct for blog/index.html
            pass
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"Checked blog index links: {filepath}")

def main():
    print("Fixing blog section links and image paths...")
    fix_blog_index_images()
    fix_blog_post_links()
    fix_blog_index_blog_links()
    print("Done!")

if __name__ == '__main__':
    main()