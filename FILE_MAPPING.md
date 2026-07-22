# FILE MAPPING: Numbered Uploads → Proper Project Structure

## Config (config/)
- asgi.py → config/asgi.py
- settings.py → config/settings.py
- urls.py → config/urls.py
- wsgi.py → config/wsgi.py

## Management Commands (apps/research/management/commands/)
- cleanup.py → apps/research/management/commands/cleanup.py
- cleanup(1).py → DELETE (duplicate)

## Templates App (apps/templates_app/)
- admin.py → apps/templates_app/admin.py
- apps.py → apps/templates_app/apps.py
- models.py → apps/templates_app/models.py
- urls(1).py → apps/templates_app/urls.py
- views.py → apps/templates_app/views.py

## Research App (apps/research/)
- admin(1).py → apps/research/admin.py
- apps(1).py → apps/research/apps.py
- models(1).py → apps/research/models.py
- tests(1).py → apps/research/tests.py
- urls(2).py → apps/research/urls.py
- views(1).py → apps/research/views.py
- chunker.py → apps/research/services/chunker.py
- job_queue.py → apps/research/services/job_queue.py
- pipeline.py → apps/research/services/pipeline.py
- search.py → apps/research/services/search.py
- summarizer.py → apps/research/services/summarizer.py

## Reports App (apps/reports/)
- admin(2).py → apps/reports/admin.py
- apps(2).py → apps/reports/apps.py
- models(2).py → apps/reports/models.py
- tests(2).py → apps/reports/tests.py
- urls(3).py → apps/reports/urls.py
- views(2).py → apps/reports/views.py
- pdf_engine.py → apps/reports/services/pdf_engine.py
- report_builder.py → apps/reports/services/report_builder.py

## History App (apps/history/)
- cleanup(1).py → apps/history/management/commands/cleanup.py (or delete if duplicate)
- admin(3).py → apps/history/admin.py
- apps(3).py → apps/history/apps.py
- models(3).py → apps/history/models.py
- urls(4).py → apps/history/urls.py
- views(3).py → apps/history/views.py

## Dashboard App (apps/dashboard/)
- admin(4).py → apps/dashboard/admin.py
- apps(4).py → apps/dashboard/apps.py
- cleanup_views.py → apps/dashboard/cleanup_views.py
- models(4).py → apps/dashboard/models.py
- urls(5).py → apps/dashboard/urls.py
- views(4).py → apps/dashboard/views.py
- views_api_keys.py → apps/dashboard/views_api_keys.py
- log_viewer.py → apps/dashboard/log_viewer.py

## Collaboration App (apps/collaboration/)
- admin(5).py → apps/collaboration/admin.py
- apps(5).py → apps/collaboration/apps.py
- models(5).py → apps/collaboration/models.py
- urls(6).py → apps/collaboration/urls.py
- views(5).py → apps/collaboration/views.py

## Accounts App (apps/accounts/)
- admin(6).py → apps/accounts/admin.py
- apps(6).py → apps/accounts/apps.py (FIXED: removed home_view, fixed signals import)
- forms.py → apps/accounts/forms.py
- models(6).py → apps/accounts/models.py
- signals.py → apps/accounts/signals.py
- tests(3).py → apps/accounts/tests.py
- urls(7).py → apps/accounts/urls.py
- views(6).py → apps/accounts/views.py

## Utils (apps/utils/)
- decorators.py → apps/utils/decorators.py
- exceptions.py → apps/utils/exceptions.py
- health.py → apps/utils/health.py
- http_client.py → apps/utils/http_client.py
- middleware.py → apps/utils/middleware.py
- rate_limit.py → apps/utils/rate_limit.py
- search_cache.py → apps/utils/search_cache.py
- tests.py → apps/utils/tests.py
- validators.py → apps/utils/validators.py

## Templates (templates/)
All .html files go to templates/pages/<app>/ or templates/includes/

## Static (static/)
- app.js → static/js/app.js
- main.css → static/css/main.css

## Root
- .env → .env
- manage.py → manage.py
- requirements.txt → requirements.txt
- run_tests.py → run_tests.py
- temp_actions.txt → DELETE (snippet file)