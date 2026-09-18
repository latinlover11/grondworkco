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

def check_performance(filepath):
    """Check basic performance metrics for an HTML file"""
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    
    # Check for viewport meta tag (mobile usability)
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if not viewport:
        issues.append("Missing viewport meta tag (mobile usability)")
    else:
        viewport_content = viewport.get('content', '')
        if 'width=device-width' not in viewport_content:
            issues.append("Viewport meta tag missing width=device-width")
        if 'initial-scale=1' not in viewport_content:
            issues.append("Viewport meta tag missing initial-scale=1")
    
    # Check for render-blocking CSS in head (should be minimal)
    css_links = soup.find_all('link', rel='stylesheet')
    for css in css_links:
        href = css.get('href', '')
        # Check if it's a Google Fonts link (usually okay)
        if 'fonts.googleapis.com' in href:
            continue
        # Check if it's loaded asynchronously or deferred (not common for CSS)
        # For now, just note if there are multiple CSS files
        pass
    
    # Check for render-blocking JS in head (should be at bottom or async/defer)
    scripts = soup.find_all('script')
    head_scripts = []
    for script in scripts:
        # Check if script is in head
        parent = script.parent
        while parent:
            if parent.name == 'head':
                head_scripts.append(script)
                break
            parent = parent.parent
    
    for script in head_scripts:
        src = script.get('src', '')
        if src:  # External script
            # Check if it has async or defer
            if not script.get('async') and not script.get('defer'):
                issues.append(f"Render-blocking JavaScript in head: {src} (consider async or defer)")
        else:  # Inline script
            # Small inline scripts are usually okay
            if len(script.string or '') > 100:  # Arbitrary threshold
                issues.append("Large inline JavaScript in head (consider moving to bottom or external file)")
    
    # Check image dimensions (width/height attributes for preventing layout shift)
    images = soup.find_all('img')
    images_without_dimensions = 0
    for img in images:
        if not img.get('width') and not img.get('height'):
            # Only warn if it's not a placeholder or very small decorative image
            src = img.get('src', '')
            if src and not src.startswith('data:') and not 'placeholder' in src.lower():
                images_without_dimensions += 1
    
    if images_without_dimensions > 0:
        issues.append(f"{images_without_dimensions} images missing width/height attributes (can cause layout shift)")
    
    # Check for compression/minification hints
    # Check if CSS/JS files are minified (simple heuristic: check for .min. in filename)
    css_links = soup.find_all('link', rel='stylesheet')
    for css in css_links:
        href = css.get('href', '')
        if href and not href.startswith('http') and not '.min.css' in href:
            issues.append(f"CSS file may not be minified: {href}")
    
    scripts = soup.find_all('script', src=True)
    for script in scripts:
        src = script.get('src', '')
        if src and not src.startswith('http') and not '.min.js' in src:
            issues.append(f"JavaScript file may not be minified: {src}")
    
    # Check for browser caching hints (via meta tags - though real caching is via HTTP headers)
    # This is just a basic check
    cache_control = soup.find('meta', attrs={'http-equiv': 'Cache-Control'})
    if not cache_control:
        # This is okay since real caching is done via HTTP headers
        pass
    
    # Check total size of page (basic)
    if len(content) > 500 * 1024:  # 500KB
        issues.append(f"Page size is large: {len(content) // 1024}KB (consider optimization)")
    
    return issues

def check_mobile_usability(filepath):
    """Check mobile-specific usability issues"""
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    soup = BeautifulSoup(content, 'html.parser')
    
    # Check for fixed-width elements that might break on mobile
    # Look for inline styles with fixed widths
    elements_with_style = soup.find_all(attrs={"style": True})
    fixed_width_count = 0
    for elem in elements_with_style:
        style = elem['style']
        if re.search(r'width:\s*\d+px', style) and not re.search(r'width:\s*0px', style):
            fixed_width_count += 1
    
    if fixed_width_count > 10:  # Arbitrary threshold
        issues.append(f"Many elements with fixed pixel widths ({fixed_width_count}) - may not be mobile-friendly")
    
    # Check for font sizes (should use relative units where possible)
    # This is more complex, so we'll skip for now
    
    # Check for touch targets (minimum 48x48px) - too complex for basic check
    
    return issues

def main():
    html_files = get_all_html_files()
    if not html_files:
        print("No HTML files found.")
        return
    
    total_perf_issues = 0
    total_mobile_issues = 0
    
    print("Running performance and mobile usability checks...\n")
    
    for filepath in html_files:
        rel_path = os.path.relpath(filepath, BASE_DIR)
        perf_issues = check_performance(filepath)
        mobile_issues = check_mobile_usability(filepath)
        
        if perf_issues or mobile_issues:
            print(f"\n{rel_path}:")
            if perf_issues:
                print("  Performance issues:")
                for issue in perf_issues:
                    print(f"    - {issue}")
                total_perf_issues += len(perf_issues)
            if mobile_issues:
                print("  Mobile usability issues:")
                for issue in mobile_issues:
                    print(f"    - {issue}")
                total_mobile_issues += len(mobile_issues)
        else:
            print(f"\n{rel_path}: No performance or mobile usability issues found.")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total performance issues: {total_perf_issues}")
    print(f"Total mobile usability issues: {total_mobile_issues}")
    
    if total_perf_issues == 0 and total_mobile_issues == 0:
        print("\n🎉 No performance or mobile usability issues detected!")
    else:
        print("\n💡 Consider addressing the issues above for better performance and mobile experience.")

if __name__ == '__main__':
    main()