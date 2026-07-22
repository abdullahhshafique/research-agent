#!/usr/bin/env python3
"""
Fix BOM (Byte Order Mark) and encoding issues in all Python files.
"""
import os
import sys


def fix_file(filepath):
    """Remove BOM and fix encoding issues in a single file."""
    with open(filepath, 'rb') as f:
        raw = f.read()

    original_len = len(raw)

    # Remove BOM if present
    if raw.startswith(b'\xef\xbb\xbf'):
        raw = raw[3:]
        print(f"  [FIXED] Removed BOM from: {filepath}")

    # Remove zero-width spaces
    raw = raw.replace(b'\xe2\x80\x8b', b'')  # U+200B
    raw = raw.replace(b'\xe2\x80\x8c', b'')  # U+200C
    raw = raw.replace(b'\xe2\x80\x8d', b'')  # U+200D

    # Replace smart quotes with straight quotes
    raw = raw.replace(b'\xe2\x80\x9c', b'"')   # left double quote
    raw = raw.replace(b'\xe2\x80\x9d', b'"')   # right double quote
    raw = raw.replace(b'\xe2\x80\x98', b"'")   # left single quote
    raw = raw.replace(b'\xe2\x80\x99', b"'")   # right single quote

    # Replace em-dash with double dash
    raw = raw.replace(b'\xe2\x80\x94', b'--')  # em-dash

    # Replace en-dash with single dash
    raw = raw.replace(b'\xe2\x80\x93', b'-')   # en-dash

    if len(raw) != original_len:
        with open(filepath, 'wb') as f:
            f.write(raw)
        return True
    return False


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    fixed_count = 0
    checked_count = 0

    print("Scanning for BOM and encoding issues...")
    print("=" * 60)

    for root, dirs, files in os.walk(project_root):
        # Skip virtual environment directories
        dirs[:] = [d for d in dirs if d not in ('myenv', 'venv', '.venv', '__pycache__', '.git')]

        for filename in files:
            if filename.endswith('.py'):
                filepath = os.path.join(root, filename)
                checked_count += 1
                if fix_file(filepath):
                    fixed_count += 1

    print("=" * 60)
    print(f"Checked: {checked_count} Python files")
    print(f"Fixed:   {fixed_count} files")

    if fixed_count > 0:
        print("\nNow run: python manage.py check")
    else:
        print("\nNo BOM issues found.")

    return 0


if __name__ == '__main__':
    sys.exit(main())