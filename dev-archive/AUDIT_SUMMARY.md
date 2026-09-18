# Site Audit Report for Groundwork Outdoor Co.

## Overview
This audit was conducted on September 17, 2025, for the Groundwork Outdoor Co. website located at `/home/los/Projects/Web-dev/grondworkco`. The audit focused on:
- Internal link validity
- Image existence and alt attributes
- JSON-LD schema markup presence
- Basic meta tags (title, description)

## Summary of Issues

### Total Issues Found: 86

### Issues by Type:
1. **Missing JSON-LD schema markup**: 14 pages
2. **Broken internal links**: 36 instances across multiple pages
3. **Missing image sources**: 12 instances
4. **Missing image alt attributes**: 11 instances
5. **Non-existent images referenced**: 5 instances

### Detailed Breakdown:

#### Pages with No Issues:
- `index.html`
- `contact.html`

#### Pages with Issues:

**about.html**
- Missing JSON-LD schema markup

**work.html**
- Image missing src attribute
- Missing JSON-LD schema markup

**testimonials.html**
- Missing JSON-LD schema markup

**case-studies/river-rock-parking-pad.html**
- Image missing src attribute
- Missing JSON-LD schema markup

**case-studies/seasonal-landscape-cleanup.html**
- Image missing src attribute
- Missing JSON-LD schema markup

**case-studies/front-yard-xeriscape.html**
- Image missing src attribute
- Missing JSON-LD schema markup

**case-studies/cedar-privacy-fence.html**
- Image not found: img/case-studies/cedar-fence-posts.jpg
- Image not found: img/case-studies/cedar-fence-rails.jpg
- Image not found: img/case-studies/cedar-fence-finished.jpg
- Image not found: img/case-studies/cedar-fence-detail.jpg
- Image missing src attribute
- Missing JSON-LD schema markup

**blog/blog-post-1.html through blog/blog-post-6.html**
- Multiple broken internal links (to ../index.html, ../work.html, etc.)
- Missing JSON-LD schema markup

**blog/index.html**
- Multiple missing images (referencing case study images with incorrect relative paths)
- Numerous broken internal links (to other blog pages and main site pages)
- Missing JSON-LD schema markup

## Recommendations

### 1. Add JSON-LD Schema Markup
All pages are missing structured data. Implement LocalBusiness schema on homepage and appropriate schemas on other pages (BlogPosting for blog posts, etc.).

### 2. Fix Broken Internal Links
- Links to `index.html#services` and `index.html#process` are actually valid (these are anchor links on the same page). The audit tool incorrectly flagged these because it was looking for separate files. These are not actually broken.
- However, many blog posts have broken relative links (e.g., `../index.html` from `blog/blog-post-1.html` should work since blog is in a subdirectory). These need to be checked and corrected.
- Blog index links to individual blog posts are broken (e.g., `blog-post-1.html` from `blog/index.html` should be `./blog-post-1.html` or `blog-post-1.html`).

### 3. Fix Image Issues
- The `work.html` page has an `<img>` tag with no `src` attribute.
- Several case study pages have `<img>` tags with no `src` attribute (likely placeholders for lightbox functionality).
- The `cedar-privacy-fence.html` page references images that don't exist in the `img/case-studies/` directory (though the base `cedar-fence.jpg` does exist).
- The blog index page is trying to load images from `../img/case-studies/` but the blog is in `/blog`, so the correct path would be `../../img/case-studies/`.

### 4. Add Missing Alt Attributes
Several `<img>` tags are missing `alt` attributes, which is important for accessibility and SEO.

## Next Steps
1. Fix the actual broken links and missing images
2. Add appropriate JSON-LD schema markup to all pages
3. Ensure all images have descriptive alt attributes
4. Verify that anchor links to sections on the same page (like `#services`) are working correctly

## Note on False Positives
The audit flagged links like `index.html#services` as "not found" because the tool was checking for a file named `index.html#services` (which doesn't exist) rather than recognizing this as an anchor link on the `index.html` page. These are not actual issues and can be ignored.

Similarly, some image `src` attributes that are empty are likely intended to be filled by JavaScript (e.g., for lightboxes) and may not represent actual missing content.