import traceback
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from .models import ModuleHealth, SystemAlert
from .utils import check_all_modules
from accounts.views import is_admin, log_action


@login_required
@user_passes_test(is_admin)
def monitoring_dashboard(request):
    if request.method == 'POST' and request.POST.get('action') == 'check':
        try:
            results = check_all_modules()
            # Create alerts for failed modules
            for module_name, result in results.items():
                if not result.get('ok', True):
                    SystemAlert.objects.create(
                        module=module_name,
                        severity='critical',
                        message=result.get('error', 'Module check failed'),
                    )
            log_action(request.user, 'HEALTH_CHECK', 'Ran system health check', request)
        except Exception as e:
            SystemAlert.objects.create(
                module='system',
                severity='critical',
                message=f'Health check failed: {str(e)}',
            )

    modules = ModuleHealth.objects.all().order_by('module_name')
    alerts = SystemAlert.objects.filter(is_resolved=False).order_by('-created_at')[:20]
    resolved_alerts = SystemAlert.objects.filter(is_resolved=True).order_by('-resolved_at')[:10]

    healthy_count = modules.filter(status='healthy').count()
    warning_count = modules.filter(status='warning').count()
    critical_count = modules.filter(status='critical').count()
    all_healthy = critical_count == 0 and warning_count == 0

    return render(request, 'monitoring/dashboard.html', {
        'modules': modules,
        'alerts': alerts,
        'resolved_alerts': resolved_alerts,
        'all_healthy': all_healthy,
        'healthy_count': healthy_count,
        'warning_count': warning_count,
        'critical_count': critical_count,
        'total_modules': modules.count(),
    })


@login_required
@user_passes_test(is_admin)
def resolve_alert(request, pk):
    if request.method == 'POST':
        alert = get_object_or_404(SystemAlert, pk=pk)
        alert.is_resolved = True
        alert.resolved_at = timezone.now()
        alert.save()
        log_action(request.user, 'RESOLVE_ALERT', f'Resolved alert #{pk}', request)
        return JsonResponse({'status': 'resolved'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
@user_passes_test(is_admin)
def module_status_api(request):
    modules = ModuleHealth.objects.all()
    data = {
        m.module_name: {
            'status': m.status,
            'message': m.message,
            'response_time': m.response_time,
            'last_checked': m.last_checked.strftime('%Y-%m-%d %H:%M:%S'),
        }
        for m in modules
    }
    return JsonResponse(data)