#!/usr/bin/env python3
import os

BASE_DIR = "/home/los/Projects/Web-dev/grondworkco"
filepath = "/home/los/Projects/Web-dev/grondworkco/blog/blog-post-1.html"
href = "../index.html"

print(f"BASE_DIR: {BASE_DIR}")
print(f"filepath: {filepath}")
print(f"href: {href}")

# Simulate what audit_site_fixed.py does
# Get the directory of the file
file_dir = os.path.dirname(filepath)
print(f"file_dir: {file_dir}")

# Resolve the link relative to the file's directory
link_path = os.path.join(file_dir, href)
print(f"link_path (relative to file): {link_path}")
print(f"exists? {os.path.exists(link_path)}")

# Now simulate what audit_site_fixed.py actually does (treating as relative to BASE_DIR)
link_path2 = os.path.join(BASE_DIR, href)
print(f"link_path2 (relative to BASE_DIR): {link_path2}")
print(f"exists? {os.path.exists(link_path2)}")

# The correct way for web link checking: resolve relative to file dir, then make relative to BASE_DIR
# Get the path of the file relative to BASE_DIR
file_rel_to_base = os.path.relpath(filepath, BASE_DIR)
print(f"file relative to BASE_DIR: {file_rel_to_base}")

# Resolve the href relative to the file's position
link_rel_to_base = os.path.normpath(os.path.join(os.path.dirname(file_rel_to_base), href))
print(f"link relative to BASE_DIR: {link_rel_to_base}")

# Now check if this exists under BASE_DIR
full_path = os.path.join(BASE_DIR, link_rel_to_base)
print(f"full path: {full_path}")
print(f"exists? {os.path.exists(full_path)}")