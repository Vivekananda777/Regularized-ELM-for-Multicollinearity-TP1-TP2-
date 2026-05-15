import time
import os
from django.db import connection
from django.conf import settings
from .models import ModuleHealth

def check_database():
    start = time.time()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        response_time = round((time.time() - start) * 1000, 2)
        ModuleHealth.objects.update_or_create(
            module_name='database',
            defaults={'status': 'healthy', 'response_time': response_time, 'message': f'DB OK in {response_time}ms'}
        )
        return True, response_time
    except Exception as e:
        ModuleHealth.objects.update_or_create(
            module_name='database',
            defaults={'status': 'critical', 'message': str(e), 'stack_trace': str(e)}
        )
        return False, None

def check_storage():
    try:
        media_root = settings.MEDIA_ROOT
        os.makedirs(media_root, exist_ok=True)
        test_file = os.path.join(media_root, '.health_check')
        with open(test_file, 'w') as f:
            f.write('ok')
        os.remove(test_file)
        free_bytes = os.statvfs(media_root).f_bavail * os.statvfs(media_root).f_frsize if hasattr(os, 'statvfs') else 0
        free_gb = round(free_bytes / (1024**3), 2)
        status = 'healthy' if free_gb > 1 else 'warning'
        ModuleHealth.objects.update_or_create(
            module_name='storage',
            defaults={'status': status, 'message': f'Storage OK. Free: {free_gb}GB'}
        )
        return True, free_gb
    except Exception as e:
        ModuleHealth.objects.update_or_create(
            module_name='storage',
            defaults={'status': 'critical', 'message': str(e)}
        )
        return False, None

def check_all_modules():
    modules_status = {}
    db_ok, db_time = check_database()
    modules_status['database'] = {'ok': db_ok, 'time': db_time}
    storage_ok, storage_free = check_storage()
    modules_status['storage'] = {'ok': storage_ok, 'free_gb': storage_free}

    app_modules = ['datasets', 'algorithms', 'diagnostics', 'dashboard', 'exports']
    for module in app_modules:
        try:
            import importlib
            importlib.import_module(f'{module}.models')
            ModuleHealth.objects.update_or_create(
                module_name=module,
                defaults={'status': 'healthy', 'message': f'{module.title()} module OK'}
            )
            modules_status[module] = {'ok': True}
        except Exception as e:
            ModuleHealth.objects.update_or_create(
                module_name=module,
                defaults={'status': 'critical', 'message': str(e), 'stack_trace': str(e)}
            )
            modules_status[module] = {'ok': False, 'error': str(e)}

    return modules_status