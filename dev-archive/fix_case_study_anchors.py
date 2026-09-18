#!/usr/bin/env python3
import os
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def fix_case_study_anchor_links():
    """Fix anchor links in case study files that point to wrong location"""
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
        
        # Fix navigation links in header
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Fix index.html#services and index.html#process
            if href == 'index.html#services':
                link['href'] = '../index.html#services'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: index.html#services -> ../index.html#services")
            elif href == 'index.html#process':
                link['href'] = '../index.html#process'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: index.html#process -> ../index.html#process")
            
            # Fix work.html#case-studies in front-yard-xeriscape.html
            elif href == 'work.html#case-studies':
                link['href'] = '../work.html#case-studies'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: work.html#case-studies -> ../work.html#case-studies")
            
            # Fix self-link in cedar-privacy-fence.html
            elif href == 'case-studies/cedar-privacy-fence.html':
                link['href'] = 'cedar-privacy-fence.html'
                modified = True
                print(f"Fixed link in {os.path.basename(filepath)}: case-studies/cedar-privacy-fence.html -> cedar-privacy-fence.html")
        
        if modified:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(str(soup))

def main():
    print("Fixing case study anchor links...")
    fix_case_study_anchor_links()
    print("Done!")

if __name__ == '__main__':
    main()