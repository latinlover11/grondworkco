#!/bin/bash

# Define the standard header template from index.html
STANDARD_HEADER='<header>
<nav class="nav">
<div class="brand">Groundwork <span>Outdoor Co.</span></div>
<div class="service-area-badge">Serving Longmont & Boulder County</div>
<ul class="nav-links">
<li><a href="/#services">Services</a></li>
<li><a href="/work.html">Our Work</a></li>
<li><a href="/about.html">About Us</a></li>
</ul>
<a class="nav-cta" href="/contact.html">Get a quote</a>
<button aria-controls="nav-mobile-panel" aria-expanded="false" aria-label="Toggle menu" class="nav-toggle" id="nav-toggle" type="button">
<span></span><span></span><span></span>
</button>
</nav>
<div class="nav-mobile-panel" id="nav-mobile-panel">
<a href="/#services">Services</a>
<a href="/work.html">Our Work</a>
<a href="/about.html">About Us</a>
</div>
</header>'

# Process each HTML file
for file in *.html blog/*.html case-studies/*.html; do
  if [[ -f "$file" ]]; then
    echo "Processing $file"
    
    # Backup original
    cp "$file" "${file}.bak"
    
    # Determine relative paths based on file location
    if [[ $file == *"blog/"* ]]; then
      # Blog files: need ../ to go up one level
      SERVICES_LINK="../index.html#services"
      WORK_LINK="../work.html"
      ABOUT_LINK="../about.html"
      TESTIMONIALS_LINK="../testimonials.html"
      CONTACT_LINK="../contact.html"
      RESOURCES_LINK="../blog/index.html"
    elif [[ $file == *"case-studies/"* ]]; then
      # Case studies: need ../../ to go up two levels
      SERVICES_LINK="../../index.html#services"
      WORK_LINK="../../work.html"
      ABOUT_LINK="../../about.html"
      TESTIMONIALS_LINK="../../testimonials.html"
      CONTACT_LINK="../../contact.html"
      RESOURCES_LINK="../../blog/index.html"
    else
      # Root files: no prefix needed
      SERVICES_LINK="/#services"
      WORK_LINK="/work.html"
      ABOUT_LINK="/about.html"
      TESTIMONIALS_LINK="/testimonials.html"
      CONTACT_LINK="/contact.html"
      RESOURCES_LINK="/blog/index.html"
    fi
    
    # Determine active link based on current file
    ACTIVE_LINK=""
    if [[ $file == "about.html" ]]; then
      ACTIVE_INDEX=2  # About Us is 3rd item (0-indexed)
    elif [[ $file == "contact.html" ]]; then
      ACTIVE_INDEX=3  # Get a quote would be 4th item, but we'll handle specially
    elif [[ $file == "work.html" ]]; then
      ACTIVE_INDEX=1  # Our Work is 2nd item
    elif [[ $file == "testimonials.html" ]]; then
      # For testimonials, we need to add it to the nav list
      ACTIVE_INDEX="testimonials"
    elif [[ $file == *"blog/"* && $file != *"blog/index.html"* ]]; then
      # Individual blog posts: active link on Resources
      ACTIVE_INDEX="resources"
    elif [[ $file == "blog/index.html" ]]; then
      # blog index: active link on Resources
      ACTIVE_INDEX="resources"
    fi
    
    # Build nav-links based on file type
    if [[ $file == *"blog/"* || $file == *"case-studies/"* ]]; then
      # These get Testimonials in nav
      if [[ "$ACTIVE_INDEX" == "testimonials" ]]; then
        NAV_LINKS="<ul class=\"nav-links\">\n<li><a href=\"$SERVICES_LINK\">Services</a></li>\n<li><a href=\"$WORK_LINK\">Our Work</a></li>\n<li><a href=\"$ABOUT_LINK\">About Us</a></li>\n<li><a href=\"$TESTIMONIALS_LINK\">Testimonials</a></li>\n<li><a class=\"active\" href=\"${TESTIMONIALS_LINK}\">Testimonials</a></li>\n</ul>"
      elif [[ "$ACTIVE_INDEX" == "resources" ]]; then
        NAV_LINKS="<ul class=\"nav-links\">\n<li><a href=\"$SERVICES_LINK\">Services</a></li>\n<li><a href=\"$WORK_LINK\">Our Work</a></li>\n<li><a href=\"$ABOUT_LINK\">About Us</a></li>\n<li><a href=\"$TESTIMONIALS_LINK\">Testimonials</a></li>\n<li><a class=\"active\" href=\"${RESOURCES_LINK}\">Resources</a></li>\n</ul>"
      else
        NAV_LINKS="<ul class=\"nav-links\">\n<li><a href=\"$SERVICES_LINK\">Services</a></li>\n<li><a href=\"$WORK_LINK\">Our Work</a></li>\n<li><a href=\"$ABOUT_LINK\">About Us</a></li>\n<li><a href=\"$TESTIMONIALS_LINK\">Testimonials</a></li>\n</ul>"
      fi
    else
      # Standard pages (index, about, contact, work)
      if [[ "$ACTIVE_INDEX" == "2" ]]; then  # About Us active
        NAV_LINKS="<ul class=\"nav-links\">\n<li><a href=\"$SERVICES_LINK\">Services</a></li>\n<li><a href=\"$WORK_LINK\">Our Work</a></li>\n<li><a class=\"active\" href=\"$ABOUT_LINK\">About Us</a></li>\n</ul>"
      elif [[ "$ACTIVE_INDEX" == "1" ]]; then  # Our Work active
        NAV_LINKS="<ul class=\"nav-links\">\n<li><a href=\"$SERVICES_LINK\">Services</a></li>\n<li><a class=\"active\" href=\"$WORK_LINK\">Our Work</a></li>\n<li><a href=\"$ABOUT_LINK\">About Us</a></li>\n</ul>"
      elif [[ "$ACTIVE_INDEX" == "3" ]]; then  # Contact active (special case)
        NAV_LINKS="<ul class=\"nav-links\">\n<li><a href=\"$SERVICES_LINK\">Services</a></li>\n<li><a href=\"$WORK_LINK\">Our Work</a></li>\n<li><a href=\"$ABOUT_LINK\">About Us</a></li>\n<li><a class=\"active\" href=\"$CONTACT_LINK\">Get a quote</a></li>\n</ul>"
      else  # No active link (index.html)
        NAV_LINKS="<ul class=\"nav-links\">\n<li><a href=\"$SERVICES_LINK\">Services</a></li>\n<li><a href=\"$WORK_LINK\">Our Work</a></li>\n<li><a href=\"$ABOUT_LINK\">About Us</a></li>\n</ul>"
      fi
    fi
    
    # Create the new header
    NEW_HEADER="<header>
<nav class=\"nav\">
<div class=\"brand\">Groundwork <span>Outdoor Co.</span></div>
<div class=\"service-area-badge\">Serving Longmont & Boulder County</div>
$NAV_LINKS
<a class=\"nav-cta\" href=\"$CONTACT_LINK\">Get a quote</a>
<button aria-controls=\"nav-mobile-panel\" aria-expanded=\"false\" aria-label=\"Toggle menu\" class=\"nav-toggle\" id=\"nav-toggle\" type=\"button\">
<span></span><span></span><span></span>
</button>
</nav>
<div class=\"nav-mobile-panel\" id=\"nav-mobile-panel\">
<a href=\"$SERVICES_LINK\">Services</a>
<a href=\"$WORK_LINK\">Our Work</a>
<a href=\"$ABOUT_LINK\">About Us</a>
</div>
</header>"
    
    # Replace header in file
    {
      # Print everything before the header
      sed -n '1,/<header>/p' "${file}.bak" | head -n -1
      # Print the new header
      echo "$NEW_HEADER"
      # Print everything after the header
      sed -n '/<\/header>/,${file}.bakp' "${file}.bak" | tail -n +2
    } > "$file"
    
    # Clean up backup
    rm "${file}.bak"
  fi
done

echo "Header standardization complete!"
