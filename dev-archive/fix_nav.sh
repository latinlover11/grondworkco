#!/bin/bash

# Fix navigation for all HTML files to match index.html format (with service-area-badge and mobile menu)
# and set active class appropriately.

# Process each HTML file
for file in *.html blog/*.html case-studies/*.html; do
  if [[ -f "$file" ]]; then
    echo "Processing $file"
    cp "$file" "${file}.bak"

    # Determine prefix based on file location
    if [[ $file == *"blog/"* ]]; then
      PREFIX="../"
    elif [[ $file == *"case-studies/"* ]]; then
      PREFIX="../../"
    else
      PREFIX=""
    fi

    # Determine active class for each of the four nav items
    active_Services=""
    active_OurWork=""
    active_Process=""
    active_AboutUs=""

    case "$file" in
      "about.html")
        active_AboutUs='class="active"'
        ;;
      "work.html")
        active_OurWork='class="active"'
        ;;
      # For index.html, contact.html, testimonials.html, blog/*, case-studies/*: no active
    esac

    # Build the nav-links string
    NAV_LINKS="<ul class=\"nav-links\">"
    NAV_LINKS="$NAV_LINKS<li><a href=\"${PREFIX}index.html#services\" $active_Services>Services</a></li>"
    NAV_LINKS="$NAV_LINKS<li><a href=\"${PREFIX}work.html\" $active_OurWork>Our Work</a></li>"
    NAV_LINKS="$NAV_LINKS<li><a href=\"${PREFIX}index.html#process\" $active_Process>Process</a></li>"
    NAV_LINKS="$NAV_LINKS<li><a href=\"${PREFIX}about.html\" $active_AboutUs>About Us</a></li>"
    NAV_LINKS="$NAV_LINKS</ul>"

    # Build the mobile panel links (no active class)
    MOBILE_LINKS=""
    MOBILE_LINKS="$MOBILE_LINKS<a href=\"${PREFIX}index.html#services\">Services</a>"
    MOBILE_LINKS="$MOBILE_LINKS<a href=\"${PREFIX}work.html\">Our Work</a>"
    MOBILE_LINKS="$MOBILE_LINKS<a href=\"${PREFIX}index.html#process\">Process</a>"
    MOBILE_LINKS="$MOBILE_LINKS<a href=\"${PREFIX}about.html\">About Us</a>"

    # Build the new header
    NEW_HEADER="<header>
<nav class=\"nav\">
<div class=\"brand\">Groundwork <span>Outdoor Co.</span></div>
<div class=\"service-area-badge\">Serving Longmont & Boulder County</div>
$NAV_LINKS
<a class=\"nav-cta\" href=\"${PREFIX}contact.html\">Get a quote</a>
<button type=\"button\" class=\"nav-toggle\" id=\"nav-toggle\" aria-label=\"Toggle menu\" aria-expanded=\"false\" aria-controls=\"nav-mobile-panel\">
<span></span><span></span><span></span>
</button>
</nav>
<div class=\"nav-mobile-panel\" id=\"nav-mobile-panel\">
$MOBILE_LINKS
</div>
</header>"

    # Use awk to replace the header
    awk -v header="$NEW_HEADER" '
      /<header>/ { 
        print header; 
        skip=1; 
        next 
      }
      /<\/header>/ { 
        skip=0; 
        next 
      }
      !skip { print }
    ' "${file}.bak" > "$file"

    # Clean up backup
    rm "${file}.bak"
  fi
done

echo "Nav fix complete!"
