#!/usr/bin/env python3
"""
Diagnose project structure issues.
"""
import os
import sys

print("=" * 60)
print("PROJECT DIAGNOSTICS")
print("=" * 60)
print(f"Python: {sys.executable}")
print(f"Working directory: {os.getcwd()}")
print(f"Python path: {sys.path[:3]}")  # First 3 entries
print()

# Check if apps is in path
print("--- Checking 'apps' package ---")
apps_path = os.path.join(os.getcwd(), 'apps')
print(f"apps/ exists: {os.path.exists(apps_path)}")
print(f"apps/__init__.py exists: {os.path.exists(os.path.join(apps_path, '__init__.py'))}")

# Check utils
utils_path = os.path.join(apps_path, 'utils')
print(f"apps/utils/ exists: {os.path.exists(utils_path)}")
print(f"apps/utils/__init__.py exists: {os.path.exists(os.path.join(utils_path, '__init__.py'))}")
print(f"apps/utils/health.py exists: {os.path.exists(os.path.join(utils_path, 'health.py'))}")

# List files in apps/utils/
if os.path.exists(utils_path):
    print(f"\nFiles in apps/utils/:")
    for f in os.listdir(utils_path):
        print(f"  {f}")
else:
    print("\n  apps/utils/ NOT FOUND!")

# Check config
config_path = os.path.join(os.getcwd(), 'config')
print(f"\n--- Checking 'config' package ---")
print(f"config/ exists: {os.path.exists(config_path)}")
print(f"config/__init__.py exists: {os.path.exists(os.path.join(config_path, '__init__.py'))}")
print(f"config/urls.py exists: {os.path.exists(os.path.join(config_path, 'urls.py'))}")

# Try importing
print("\n--- Import Test ---")
try:
    import apps
    print("import apps: SUCCESS")
except Exception as e:
    print(f"import apps: FAILED - {e}")

try:
    import apps.utils
    print("import apps.utils: SUCCESS")
except Exception as e:
    print(f"import apps.utils: FAILED - {e}")

try:
    from apps.utils.health import health_check
    print("from apps.utils.health import health_check: SUCCESS")
except Exception as e:
    print(f"from apps.utils.health import health_check: FAILED - {e}")

# Check if project root is in sys.path
print(f"\n--- sys.path check ---")
if os.getcwd() in sys.path or '' in sys.path:
    print("Current directory IS in sys.path: OK")
else:
    print("Current directory NOT in sys.path: PROBLEM")