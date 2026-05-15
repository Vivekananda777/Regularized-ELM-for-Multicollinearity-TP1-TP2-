from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import CustomUser, AuditLog
from .forms import LoginForm, CustomUserCreationForm, UserEditForm, RegisterForm


def is_admin(user):
    return user.is_authenticated and (user.role == 'admin' or user.is_superuser)


def can_train(user):
    return user.is_authenticated and user.can_train()


def can_upload(user):
    return user.is_authenticated and user.can_upload()


def log_action(user, action, details='', request=None):
    ip = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    AuditLog.objects.create(user=user, action=action, details=details, ip_address=ip)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated. Contact admin.')
                return render(request, 'accounts/login.html', {'form': form})
            login(request, user)
            log_action(user, 'LOGIN', 'User logged in', request)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    from .forms import RegisterForm
    form = RegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.role = 'analyst'
            user.save()
            log_action(user, 'REGISTER', f'New user registered: {user.username}', request)
            messages.success(
                request,
                f'Account created successfully! Welcome, {user.first_name}. Please log in.'
            )
            return redirect('accounts:login')
        else:
            messages.error(request, 'Please fix the errors below and try again.')

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def logout_view(request):
    log_action(request.user, 'LOGOUT', 'User logged out', request)
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


@login_required
@user_passes_test(is_admin)
def user_management(request):
    users = CustomUser.objects.all().order_by('-created_at')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    if role_filter:
        users = users.filter(role=role_filter)
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    return render(request, 'accounts/user_management.html', {
        'users': users,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'role_choices': CustomUser.ROLE_CHOICES,
    })


@login_required
@user_passes_test(is_admin)
def create_user(request):
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        log_action(request.user, 'CREATE_USER', f'Created user: {user.username}', request)
        messages.success(request, f'User "{user.username}" created successfully.')
        return redirect('accounts:user_management')
    return render(request, 'accounts/user_form.html', {'form': form, 'title': 'Create New User'})


@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    form = UserEditForm(request.POST or None, instance=user_obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request.user, 'EDIT_USER', f'Edited user: {user_obj.username}', request)
        messages.success(request, f'User "{user_obj.username}" updated successfully.')
        return redirect('accounts:user_management')
    return render(request, 'accounts/user_form.html', {
        'form': form,
        'title': f'Edit User — {user_obj.username}',
        'user_obj': user_obj
    })


@login_required
@user_passes_test(is_admin)
def revoke_access(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    if user_obj == request.user:
        messages.error(request, 'You cannot revoke your own access.')
        return redirect('accounts:user_management')
    user_obj.is_active = False
    user_obj.save()
    log_action(request.user, 'REVOKE_ACCESS', f'Revoked: {user_obj.username}', request)
    messages.warning(request, f'Access revoked for "{user_obj.username}".')
    return redirect('accounts:user_management')


@login_required
@user_passes_test(is_admin)
def restore_access(request, user_id):
    user_obj = get_object_or_404(CustomUser, id=user_id)
    user_obj.is_active = True
    user_obj.save()
    log_action(request.user, 'RESTORE_ACCESS', f'Restored: {user_obj.username}', request)
    messages.success(request, f'Access restored for "{user_obj.username}".')
    return redirect('accounts:user_management')


@login_required
@user_passes_test(is_admin)
def audit_log(request):
    logs = AuditLog.objects.select_related('user').all()
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')
    date_filter = request.GET.get('date', '')
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    if action_filter:
        logs = logs.filter(action__icontains=action_filter)
    if date_filter:
        logs = logs.filter(timestamp__date=date_filter)
    return render(request, 'accounts/audit_log.html', {
        'logs': logs[:500],
        'user_filter': user_filter,
        'action_filter': action_filter,
        'date_filter': date_filter,
        'total': logs.count(),
    })


@login_required
def profile(request):
    recent_logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')[:10]
    return render(request, 'accounts/profile.html', {
        'user_obj': request.user,
        'recent_logs': recent_logs,
    })