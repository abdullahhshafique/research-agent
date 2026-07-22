import os
import sys
import django

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    django.setup()
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2)
    
    failures = test_runner.run_tests([
        'apps.accounts.tests',
        'apps.research.tests',
        'apps.reports.tests',
        'apps.utils.tests',
    ])
    
    sys.exit(bool(failures))