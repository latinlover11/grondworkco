#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def fix_case_study_image_paths():
    """Fix image paths in case study HTML files"""
    case_studies_dir = os.path.join(BASE_DIR, 'case-studies')
    case_studies = []
    
    # Get all case study HTML files
    for file in os.listdir(case_studies_dir):
        if file.endswith('.html'):
            case_studies.append(os.path.join(case_studies_dir, file))
    
    for filepath in case_studies:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        modified = False
        
        # Find all images
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and src.startswith('img/case-studies/'):
                # The case studies are in case-studies/ subdirectory
                # So we need to go up one level to get to img/
                new_src = '../' + src
                img['src'] = new_src
                print(f"Fixed image src in {os.path.basename(filepath)}: {src} -> {new_src}")
                modified = True
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))

def fix_case_study_links():
    """Fix links in case study files that point to wrong directories"""
    case_studies_dir = os.path.join(BASE_DIR, 'case-studies')
    case_studies = []
    
    # Get all case study HTML files
    for file in os.listdir(case_studies_dir):
        if file.endswith('.html'):
            case_studies.append(os.path.join(case_studies_dir, file))
    
    for filepath in case_studies:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        modified = False
        
        # Fix navigation links
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # From case-studies/page.html, we need ../ to reach root
            if href == 'index.html':
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
            elif href == 'contact.html':
                link['href'] = '../contact.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: contact.html -> ../contact.html")
            elif href == 'testimonials.html':
                link['href'] = '../testimonials.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: testimonials.html -> ../testimonials.html")
        
        # Also fix internal case study links (like in cedar-privacy-fence.html)
        for link in soup.find_all('a', href=True):
            href = link['href']
            # Skip if already fixed or is an anchor/external link
            if href.startswith('#') or href.startswith('http://') or href.startswith('https://') or href.startswith('../'):
                continue
            # If it's a link to another case study, fix the path
            if href.endswith('.html') and href not in ['index.html', 'work.html', 'about.html', 'contact.html', 'testimonials.html']:
                # Check if it's in the same directory
                link_path = os.path.join(os.path.dirname(filepath), href)
                if os.path.exists(link_path):
                    # It's in the same directory, so we need to make it relative from case-studies/
                    link['href'] = href  # Already correct
                else:
                    # Try to find it in case-studies directory
                    cs_path = os.path.join(case_studies_dir, href)
                    if os.path.exists(cs_path):
                        # It's in case-studies/, so we need ../case-studies/ from the case study page
                        link['href'] = '../case-studies/' + href
                        modified = True
                        print(f"Fixed case study link in {os.path.basename(filepath)}: {href} -> ../case-studies/{href}")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))

def fix_blog_index_image_paths():
    """Fix image paths in blog/index.html (again, to make sure)"""
    filepath = os.path.join(BASE_DIR, 'blog', 'index.html')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    modified = False
    
    # Find all images in blog index
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and src.startswith('../../img/case-studies/'):
            # Fix the path: blog/index.html is in blog/, need to go up one level to reach img/
            new_src = src.replace('../../img/case-studies/', '../img/case-studies/')
            img['src'] = new_src
            print(f"Fixed image src in blog/index.html: {src} -> {new_src}")
            modified = True
    
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
    else:
        print("blog/index.html image paths already correct or no changes needed")

def main():
    print("Fixing case study image paths and links...")
    fix_case_study_image_paths()
    fix_case_study_links()
    fix_blog_index_image_paths()
    print("Done!")

if __name__ == '__main__':
    main()