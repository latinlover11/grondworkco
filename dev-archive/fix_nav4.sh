#!/bin/bash

# Fix navigation for all HTML files to match index.html format

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
    
    # Define the base nav items and their hrefs
    declare -A ITEMS
    ITEMS[Services]="${PREFIX}index.html#services"
    ITEMS[Our Work]="${PREFIX}work.html"
    ITEMS[Process]="${PREFIX}index.html#process"
    ITEMS[About Us]="${PREFIX}about.html"
    ITEMS[Testimonials]="${PREFIX}testimonials.html"
    ITEMS[Resources]="${PREFIX}blog/index.html"
    
    # Determine extra items and active item based on file type
    EXTRA=()  # extra items to append after base
    ACTIVE="" # the item that should be active
    
    case "$file" in
      "about.html")
        ACTIVE="About Us"
        ;;
      "work.html")
        ACTIVE="Our Work"
        ;;
      "testimonials.html")
        EXTRA=("Testimonials")
        ACTIVE="Testimonials"
        ;;
      *"blog/"*)
        # For blog files, we add Testimonials and Resources, and set Resources active
        EXTRA=("Testimonials" "Resources")
        ACTIVE="Resources"
        ;;
      *"case-studies/"*)
        # For case studies, we set Our Work active
        ACTIVE="Our Work"
        ;;
      "contact.html")
        # No active nav-item
        ;;
      "index.html")
        # No active nav-item
        ;;
      *)
        # Default: no active
        ;;
    esac
    
    # Build the nav-links string
    NAV_LINKS=""
    # First, the base items in order
    for ITEM in Services "Our Work" Process "About Us"; do
      HREF=${ITEMS[$ITEM]}
      if [[ "$ITEM" == "$ACTIVE" ]]; then
        NAV_LINKS="$NAV_LINKS<li><a class=\"active\" href=\"$HREF\">$ITEM</a></li>"
      else
        NAV_LINKS="$NAV_LINKS<li><a href=\"$HREF\">$ITEM</a></li>"
      fi
    done
    # Then, the extra items
    for ITEM in "${EXTRA[@]}"; do
      HREF=${ITEMS[$ITEM]}
      if [[ "$ITEM" == "$ACTIVE" ]]; then
        NAV_LINKS="$NAV_LINKS<li><a class=\"active\" href=\"$HREF\">$ITEM</a></li>"
      else
        NAV_LINKS="$NAV_LINKS<li><a href=\"$HREF\">$ITEM</a></li>"
      fi
    done
    
    # Wrap in ul
    NAV_LINKS="<ul class=\"nav-links\">$NAV_LINKS</ul>"
    
    # Build the mobile panel (always the four base items, no active)
    MOBILE_LINKS=""
    for ITEM in Services "Our Work" Process "About Us"; do
      HREF=${ITEMS[$ITEM]}
      MOBILE_LINKS="$MOBILE_LINKS<a href=\"$HREF\">$ITEM</a>"
    done
    
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
$MOBILE_LINKS
</div>
</header>"
    
    # Find the start and end lines of the header
    START_LINE=$(grep -n '<header>' "${file}.bak" | head -1 | cut -d: -f1)
    END_LINE=$(grep -n '</header>' "${file}.bak" | head -1 | cut -d: -f1)
    
    # If we didn't find the header, skip the file
    if [[ -z "$START_LINE" || -z "$END_LINE" ]]; then
      echo "Warning: Could not find header in $file"
      rm "${file}.bak"
      continue
    fi
    
    # Create the new file
    {
      # Print lines before the header
      sed -n "1,$((START_LINE-1))p" "${file}.bak"
      # Print the new header
      echo "$NEW_HEADER"
      # Print lines after the header
      sed -n "$((END_LINE+1)),\$p" "${file}.bak"
    } > "$file"
    
    # Clean up backup
    rm "${file}.bak"
  fi
done

echo "Nav fix complete!"
