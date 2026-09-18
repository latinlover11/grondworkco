#!/usr/bin/env python3
import os

BASE_DIR = "/home/los/Projects/Web-dev/grondworkco"
filepath = "/home/los/Projects/Web-dev/grondworkco/case-studies/river-rock-parking-pad.html"
src = "../img/case-studies/river-rock-after.jpg"

print(f"BASE_DIR: {BASE_DIR}")
print(f"filepath: {filepath}")
print(f"src: {src}")

# Simulate what audit_site_final.py does
def resolve_path(base_dir, file_path, link_href):
    """
    Resolve a link href relative to the file's path, then check if it exists under base_dir.
    This mimics how browsers resolve links.
    """
    # Get the directory containing the file
    file_dir = os.path.dirname(file_path)
    print(f"file_dir: {file_dir}")
    
    # Resolve the link relative to the file's directory
    # This handles ../ and ./ correctly
    absolute_link_path = os.path.normpath(os.path.join(file_dir, link_href))
    print(f"absolute_link_path: {absolute_link_path}")
    
    # Now check if this path exists under the base_dir
    # If the resolved path is already under base_dir, use it as-is
    # If it's outside, we still check it (for cases like linking outside the site)
    return absolute_link_path

resolved = resolve_path(BASE_DIR, filepath, src)
print(f"resolved path: {resolved}")
print(f"exists? {os.path.exists(resolved)}")

# Also check the direct approach
direct_path = os.path.join(BASE_DIR, src.lstrip('/') if src.startswith('/') else src)
print(f"direct_path: {direct_path}")
print(f"direct_path exists? {os.path.exists(direct_path)}")

# And the file-relative approach
file_dir = os.path.dirname(filepath)
file_relative_path = os.path.normpath(os.path.join(file_dir, src))
print(f"file_relative_path: {file_relative_path}")
print(f"file_relative_path exists? {os.path.exists(file_relative_path)}")