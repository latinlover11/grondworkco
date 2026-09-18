#!/bin/bash

# Standardize navigation headers across all HTML files

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

    # Determine active item and extra items
    ACTIVE_ITEM=""  # will be one of: Services, Our Work, Process, About Us, Testimonials, Resources
    EXTRA_ITEMS=()  # additional nav items beyond the base four

    case "$file" in
      "about.html")
        ACTIVE_ITEM="About Us"
        ;;
      "work.html")
        ACTIVE_ITEM="Our Work"
        ;;
      "testimonials.html")
        EXTRA_ITEMS=("Testimonials")
        ACTIVE_ITEM="Testimonials"
        ;;
      *"blog/"*)
        # For blog files, we add Testimonials and Resources, and set Resources active
        EXTRA_ITEMS=("Testimonials" "Resources")
        ACTIVE_ITEM="Resources"
        ;;
      *"case-studies/"*)
        # For case studies, we set Our Work active
        ACTIVE_ITEM="Our Work"
        ;;
      "contact.html")
        # No active nav item
        ;;
      "index.html")
        # No active nav item
        ;;
      *)
        # Default: no active
        ;;
    esac

    # Base items (always present)
    BASE_ITEMS=("Services" "Our Work" "Process" "About Us")

    # Build the desktop nav-links (<ul> ... </ul>)
    NAV_LINKS=""
    for ITEM in "${BASE_ITEMS[@]}"; do
      # Determine href for this item
      case "$ITEM" in
        "Services") HREF="${PREFIX}index.html#services" ;;
        "Our Work") HREF="${PREFIX}work.html" ;;
        "Process") HREF="${PREFIX}index.html#process" ;;
        "About Us") HREF="${PREFIX}about.html" ;;
      esac
      if [[ "$ITEM" == "$ACTIVE_ITEM" ]]; then
        NAV_LINKS="$NAV_LINKS<li><a class=\"active\" href=\"$HREF\">$ITEM</a></li>"
      else
        NAV_LINKS="$NAV_LINKS<li><a href=\"$HREF\">$ITEM</a></li>"
      fi
    done

    # Add extra items
    for ITEM in "${EXTRA_ITEMS[@]}"; do
      case "$ITEM" in
        "Testimonials") HREF="${PREFIX}testimonials.html" ;;
        "Resources") HREF="${PREFIX}blog/index.html" ;;
      esac
      if [[ "$ITEM" == "$ACTIVE_ITEM" ]]; then
        NAV_LINKS="$NAV_LINKS<li><a class=\"active\" href=\"$HREF\">$ITEM</a></li>"
      else
        NAV_LINKS="$NAV_LINKS<li><a href=\"$HREF\">$ITEM</a></li>"
      fi
    done

    NAV_LINKS="<ul class=\"nav-links\">$NAV_LINKS</ul>"

    # Build the mobile panel links (just the <a> tags for base items, no active)
    MOBILE_LINKS=""
    for ITEM in "${BASE_ITEMS[@]}"; do
      case "$ITEM" in
        "Services") HREF="${PREFIX}index.html#services" ;;
        "Our Work") HREF="${PREFIX}work.html" ;;
        "Process") HREF="${PREFIX}index.html#process" ;;
        "About Us") HREF="${PREFIX}about.html" ;;
      esac
      MOBILE_LINKS="$MOBILE_LINKS<a href=\"$HREF\">$ITEM</a>"
    done

    # Build the new header
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

    # Replace the header using awk
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