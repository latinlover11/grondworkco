#!/bin/bash

# Fix navigation for all HTML files

# Process each HTML file
for file in *.html blog/*.html case-studies/*.html; do
  if [[ -f "$file" ]]; then
    echo "Processing $file"
    
    # Backup original
    cp "$file" "${file}.bak"
    
    # Determine relative paths based on file location
    if [[ $file == *"blog/"* ]]; then
      # Blog files: need ../ to go up one level
      PREFIX="../"
    elif [[ $file == *"case-studies/"* ]]; then
      # Case studies: need ../../ to go up two levels
      PREFIX="../../"
    else
      # Root files: no prefix needed
      PREFIX=""
    fi
    
    # Determine active link and extra links based on file type
    ACTIVE_INDEX=""  # index of the li to make active (0-based) in the base nav
    EXTRA_NAV=""     # extra nav items to append after the base nav
    
    # Base nav-links (without active class) for the four standard items
    BASE_NAV='<li><a href="/index.html#services">Services</a></li>
<li><a href="/work.html">Our Work</a></li>
<li><a href="/index.html#process">Process</a></li>
<li><a href="/about.html">About Us</a></li>'
    
    if [[ $file == "testimonials.html" ]]; then
      # For testimonials, we add Testimonials after About Us and set it active
      EXTRA_NAV='<li><a class="active" href="'"$PREFIX"'testimonials.html">Testimonials</a></li>'
    elif [[ $file == *"blog/"* ]]; then
      # For blog files, we add Testimonials and Resources after About Us, and set Resources active
      EXTRA_NAV='<li><a href="'"$PREFIX"'testimonials.html">Testimonials</a></li>
<li><a class="active" href="'"$PREFIX"'blog/index.html">Resources</a></li>'
    elif [[ $file == *"case-studies/"* ]]; then
      # For case studies, we set Our Work active (second item in base nav, index 1)
      ACTIVE_INDEX=1
    else
      # Root files: set active based on filename
      case "$file" in
        "about.html")
          ACTIVE_INDEX=3  # About Us is the 4th item (0-indexed 3)
          ;;
        "work.html")
          ACTIVE_INDEX=1  # Our Work is the 2nd item (0-indexed 1)
          ;;
        "contact.html")
          # No active nav-link (contact is a CTA)
          ;;
        "index.html")
          # No active nav-link
          ;;
        *)
          # Default: no active
          ;;
      esac
    fi
    
    # If we have an active index, we need to modify the base nav to add the active class
    if [[ -n "$ACTIVE_INDEX" ]]; then
      # We'll split the base nav into lines, add active class to the specified index, and reassemble
      # We'll use a temporary file to hold the base nav lines
      echo "$BASE_NAV" > /tmp/base_nav.txt
      
      # Read each line and add active class to the matching index
      NAV_LINKS=""
      index=0
      while IFS= read -r line; do
        if [[ $index -eq $ACTIVE_INDEX ]]; then
          # Add class="active" to the <a> tag in this line
          # We assume the line contains <a href=...> and we want to insert class="active" after the href
          line=$(echo "$line" | sed 's/<a href=/<a class="active" href=/')
        fi
        NAV_LINKS="$NAV_LINKS$line"$'\n'
        ((index++))
      done < /tmp/base_nav.txt
      
      # Clean up
      rm -f /tmp/base_nav.txt
    else
      NAV_LINKS="$BASE_NAV"
    fi
    
    # Append extra nav items if any
    if [[ -n "$EXTRA_NAV" ]]; then
      # We need to insert the extra nav items after the base nav (before the closing </ul> in the template)
      # We'll handle this by adding to the nav_links string before we wrap in <ul>
      # For simplicity, we'll just append the extra nav items to the nav_links string and then wrap in <ul> later.
      NAV_LINKS="$NAV_LINKS$EXTRA_NAV"
    fi
    
    # Wrap the nav-links in <ul> tags
    NAV_LINKS="<ul class=\"nav-links\">$NAV_LINKS</ul>"
    
    # Create the new header
    NEW_HEADER="<header>
<nav class=\"nav\">
<div class=\"brand\">Groundwork <span>Outdoor Co.</span></div>
<div class=\"service-area-badge\">Serving Longmont & Boulder County</div>
$NAV_LINKS
<a class=\"nav-cta\" href=\"${PREFIX}contact.html\">Get a quote</a>
<button aria-controls=\"nav-mobile-panel\" aria-expanded=\"false\" aria-label=\"Toggle menu\" class=\"nav-toggle\" id=\"nav-toggle\" type=\"button\">
<span></span><span></span><span></span>
</button>
</nav>
<div class=\"nav-mobile-panel\" id=\"nav-mobile-panel\">
<a href=\"${PREFIX}index.html#services\">Services</a>
<a href=\"${PREFIX}work.html\">Our Work</a>
<a href=\"${PREFIX}index.html#process\">Process</a>
<a href=\"${PREFIX}about.html\">About Us</a>
</div>
</header>"
    
    # Replace header in file
    {
      # Print everything before the header
      sed -n '1,/<header>/p' "${file}.bak" | head -n -1
      # Print the new header
      echo "$NEW_HEADER"
      # Print everything after the header (from the closing header tag to the end)
      sed -n '/<\/header>/,${file}.bakp' "${file}.bak" | tail -n +2
    } > "$file"
    
    # Clean up backup
    rm "${file}.bak"
  fi
done

echo "Nav fix complete!"