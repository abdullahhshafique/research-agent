# AI Research Agent - Day 1 Fix Installation Guide

## Critical Issue Found: BOM (Byte Order Mark) in Python Files

Your error:
```
SyntaxError: invalid non-printable character U+FEFF
```

This means 44 of your Python files have a hidden BOM character at the start. This happens when files are saved with "UTF-8 with BOM" encoding (common on Windows).

## Step 1: Run the BOM Fix Script

1. Copy `fix_bom.py` to your project root (`E:\Linkedin Project\Research-agent\ai_research_agent`)
2. Run it:
```powershell
cd "E:\Linkedin Project\Research-agent\ai_research_agent"
python fix_bom.py
```

This will automatically scan ALL `.py` files and remove BOM characters.

## Step 2: Verify the Fix

After running fix_bom.py, test:
```powershell
python manage.py check
```

If you see `System check identified no issues`, the BOM problem is fixed.

## Step 3: Apply Template Fixes

Copy these fixed templates to `templates/pages/accounts/`:
- `password_reset.html` → replace existing
- `password_reset_done.html` → replace existing  
- `register.html` → replace existing
- `password_reset_complete.html` → replace existing

Copy to `templates/pages/dashboard/`:
- `user_management.html` → replace existing

Copy to `templates/pages/templates/`:
- `list_templates.html` → rename to `list.html`, replace existing

## Step 4: Apply Python Fixes

Copy these to `apps/accounts/`:
- `apps_accounts.py` → rename to `apps.py`, replace existing

Copy to `apps/dashboard/`:
- `views_dashboard.py` → rename to `views.py`, replace existing

## Step 5: Create __init__.py Files

Create empty `__init__.py` files in these directories (if they don't exist):
```
apps/
apps/accounts/
apps/research/
apps/research/services/
apps/reports/
apps/reports/services/
apps/history/
apps/collaboration/
apps/templates_app/
apps/dashboard/
apps/dashboard/services/
apps/utils/
```

You can do this quickly in PowerShell:
```powershell
$dirs = @("apps", "apps/accounts", "apps/research", "apps/research/services", "apps/reports", "apps/reports/services", "apps/history", "apps/collaboration", "apps/templates_app", "apps/dashboard", "apps/dashboard/services", "apps/utils")
foreach ($d in $dirs) { New-Item -ItemType File -Path "$d/__init__.py" -Force }
```

## Step 6: Clean Model Files

The cleaned model files (BOM removed) are provided:
- `models_collaboration_clean.py` → `apps/collaboration/models.py`
- `models_clean.py` → `apps/templates_app/models.py`
- `models_1_clean.py` → `apps/research/models.py`
- `models_2_clean.py` → `apps/reports/models.py`
- `models_3_clean.py` → `apps/history/models.py`
- `models_4_clean.py` → `apps/dashboard/models.py`
- `models_6_clean.py` → `apps/accounts/models.py`

## Step 7: Final Verification

```powershell
python manage.py check
python manage.py migrate --check
```

If both pass without errors, Day 1 fixes are complete!

## What Was Fixed

| Issue | Count | Description |
|-------|-------|-------------|
| BOM in Python files | 44 files | Hidden U+FEFF character causing SyntaxError |
| Broken URL tags | 4 templates | Double closing braces `}}` in `{% url %}` |
| Missing URL namespace | 1 template | `template_use` missing `templates:` prefix |
| Hardcoded API endpoints | 1 template | User management JS using wrong URL paths |
| Missing `__init__.py` | 12 packages | Python packages unimportable without them |
| Wrong import path | 1 view | `log_viewer` imported from non-existent `services/` |
| `home_view` in apps.py | 1 app | View function misplaced in AppConfig class |

## Next: Day 2 Fixes

After Day 1 is verified working, Day 2 will address:
- Service file organization (chunker, search, summarizer need proper `services/` subdirectories)
- WhiteNoise for production static files
- Health check enhancement
- "Save as Template" feature
