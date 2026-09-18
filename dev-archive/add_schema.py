#!/usr/bin/env python3
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_all_html_files():
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    return html_files

def get_page_type(filepath):
    """Determine the type of page for schema markup."""
    rel_path = os.path.relpath(filepath, BASE_DIR)
    if rel_path.startswith('blog/'):
        if os.path.basename(filepath) == 'index.html':
            return 'blog_index'
        else:
            return 'blog_post'
    else:
        return 'local_business'

def generate_local_business_jsonld(page_url=None):
    """Generate LocalBusiness JSON-LD."""
    # Use the business homepage URL for @id and url
    business_url = "https://groundworkoutdoor.co/"
    if page_url:
        # Use the page URL for the 'url' property, but keep @id as the business homepage
        url = page_url
    else:
        url = business_url
    
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "Groundwork Outdoor Co.",
        "image": [
            "https://groundworkoutdoor.co/img/logo.png",  # We'll need to check if this exists
            "https://groundworkoutdoor.co/img/og-image.jpg"
        ],
        "@id": business_url,
        "url": url,
        "telephone": "+15550194420",
        "priceRange": "$$$",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "123 Main St",
            "addressLocality": "Longmont",
            "postalCode": "80501",
            "addressRegion": "CO",
            "addressCountry": "US"
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": 40.1672,
            "longitude": -105.1019
        },
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday"
                ],
                "opens": "08:00",
                "closes": "17:00"
            }
        ],
        "servesArea": {
            "@type": "Place",
            "name": "Longmont and Boulder County, CO"
        },
        "department": [
            {
                "@type": "Landscaper",
                "name": "Groundwork Outdoor Co. Hardscaping",
                "url": f"{business_url}#services"
            },
            {
                "@type": "HomeAndConstructionBusiness",
                "name": "Groundwork Outdoor Co. Fencing",
                "url": f"{business_url}#services"
            },
            {
                "@type": "Gardener",
                "name": "Groundwork Outdoor Co. Lawn Care",
                "url": f"{business_url}#services"
            }
        ],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Services",
            "itemListElement": [
                {
                    "@type": "Offer",
                    "name": "Hardscaping & Patios",
                    "description": "Custom patios, walkways, retaining walls, and outdoor kitchens",
                    "url": f"{business_url}#services"
                },
                {
                    "@type": "Offer",
                    "name": "Fencing Installation & Repair",
                    "description": "Cedar privacy fences, ornamental steel, and custom gates",
                    "url": f"{business_url}#services"
                },
                {
                    "@type": "Offer",
                    "name": "Lawn Maintenance & Care",
                    "description": "Weekly mowing, aeration, fertilization, and seasonal cleanups",
                    "url": f"{business_url}#services"
                }
            ]
        }
    }

def generate_blog_posting_jsonld(soup, page_url):
    """Generate BlogPosting JSON-LD from a blog post page."""
    # Try to get title from <h1> or <title>
    title_tag = soup.find('h1')
    if not title_tag:
        title_tag = soup.find('title')
    headline = title_tag.get_text().strip() if title_tag else "Groundwork Outdoor Co. Blog Post"
    
    # Get description from meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc.get('content', '').strip() if meta_desc else ""
    
    # Try to get the first image in the main content
    image_url = None
    # Look for images in common content areas
    content_selectors = ['.blog-content', '.wrap', 'article', 'main']
    for selector in content_selectors:
        container = soup.select_one(selector)
        if container:
            img = container.find('img')
            if img and img.get('src'):
                src = img['src']
                # Make absolute URL
                if not src.startswith('http'):
                    src = urljoin(page_url, src)
                image_url = src
                break
    
    # If no image found, use a default
    if not image_url:
        image_url = "https://groundworkoutdoor.co/img/og-image.jpg"
    
    # Try to get date from the page (if available)
    # We'll look for a time element or a date pattern
    date_published = None
    time_tag = soup.find('time')
    if time_tag and time_tag.get('datetime'):
        date_published = time_tag['datetime']
    else:
        # Look for any element with a date-like class or text
        date_elements = soup.find_all(class_=re.compile(r'date|time', re.I))
        for el in date_elements:
            text = el.get_text().strip()
            # Simple pattern for YYYY-MM-DD
            if re.match(r'\d{4}-\d{2}-\d{2}', text):
                date_published = text
                break
    
    # Author
    author = {
        "@type": "Organization",
        "name": "Groundwork Outdoor Co."
    }
    
    result = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": headline,
        "description": description,
        "image": image_url,
        "author": author,
        "publisher": {
            "@type": "Organization",
            "name": "Groundwork Outdoor Co.",
            "logo": {
                "@type": "ImageObject",
                "url": "https://groundworkoutdoor.co/img/logo.png"
            }
        },
        "url": page_url
    }
    
    if date_published:
        result["datePublished"] = date_published
    
    return result

def insert_jsonld(soup, jsonld_data):
    """Insert or replace JSON-LD in the soup."""
    # Remove existing JSON-LD scripts
    for script in soup.find_all('script', type='application/ld+json'):
        script.decompose()
    
    # Create new script tag
    script_tag = soup.new_tag('script', type='application/ld+json')
    script_tag.string = str(jsonld_data).replace("'", '"')  # Ensure double quotes
    # Pretty print the JSON for readability
    import json
    script_tag.string = json.dumps(jsonld_data, indent=2)
    
    # Insert before closing head tag
    head = soup.find('head')
    if head:
        head.append(script_tag)
    else:
        # If no head, insert at the beginning
        soup.insert(0, script_tag)
    
    return soup

def process_file(filepath):
    """Process a single HTML file."""
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    # Determine page type
    page_type = get_page_type(filepath)
    
    # Get the page URL (for canonical URL in JSON-LD)
    rel_path = os.path.relpath(filepath, BASE_DIR)
    # Convert to URL path
    url_path = '/' + rel_path.replace(os.sep, '/')
    page_url = f"https://groundworkoutdoor.co{url_path}"
    
    # Generate JSON-LD based on type
    if page_type == 'local_business':
        jsonld_data = generate_local_business_jsonld(page_url=page_url)
    elif page_type == 'blog_index':
        jsonld_data = generate_local_business_jsonld(page_url=page_url)
    elif page_type == 'blog_post':
        jsonld_data = generate_blog_posting_jsonld(soup, page_url)
    else:
        jsonld_data = generate_local_business_jsonld(page_url=page_url)
    
    # Insert JSON-LD
    soup = insert_jsonld(soup, jsonld_data)
    
    # Write back to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(soup))
    
    print(f"  -> Added JSON-LD for {page_type}")

def main():
    html_files = get_all_html_files()
    for filepath in html_files:
        process_file(filepath)
    print("Schema markup added to all pages.")

if __name__ == '__main__':
    main()