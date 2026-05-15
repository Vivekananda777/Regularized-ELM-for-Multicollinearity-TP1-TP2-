from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from algorithms.models import TrainingResult, AlgorithmConfig
from algorithms.utils import train_and_evaluate
from datasets.models import Dataset
from datasets.utils import load_dataset
from accounts.models import CustomUser
from accounts.views import is_admin, log_action
from .models import BenchmarkJob


@login_required
def home(request):
    results = TrainingResult.objects.filter(
        status='completed'
    ).select_related('dataset', 'algorithm_config')

    total_datasets = Dataset.objects.filter(status='active').count()
    total_algorithms = AlgorithmConfig.objects.filter(status='enabled').count()
    total_results = results.count()
    failed_results = TrainingResult.objects.filter(status='failed').count()
    recent_results = results.order_by('-created_at')[:6]

    # Best performers
    best_clf = results.filter(accuracy__isnull=False).order_by('-accuracy').first()
    best_reg = results.filter(rmse__isnull=False).order_by('rmse').first()

    return render(request, 'dashboard/home.html', {
        'total_datasets': total_datasets,
        'total_algorithms': total_algorithms,
        'total_results': total_results,
        'failed_results': failed_results,
        'recent_results': recent_results,
        'best_clf': best_clf,
        'best_reg': best_reg,
    })


@login_required
def performance_dashboard(request):
    results = TrainingResult.objects.filter(
        status='completed'
    ).select_related('dataset', 'algorithm_config', 'user').order_by('-created_at')

    dataset_filter = request.GET.get('dataset', '')
    algo_filter = request.GET.get('algorithm', '')
    task_filter = request.GET.get('task', '')

    if dataset_filter:
        results = results.filter(dataset__id=dataset_filter)
    if algo_filter:
        results = results.filter(algorithm_config__id=algo_filter)
    if task_filter:
        results = results.filter(dataset__task_type=task_filter)

    datasets = Dataset.objects.filter(status='active')
    algorithms = AlgorithmConfig.objects.filter(status='enabled')

    # Highlight best per metric
    best_accuracy = results.filter(accuracy__isnull=False).order_by('-accuracy').values_list('id', flat=True).first()
    best_f1 = results.filter(f1_score__isnull=False).order_by('-f1_score').values_list('id', flat=True).first()
    best_rmse = results.filter(rmse__isnull=False).order_by('rmse').values_list('id', flat=True).first()
    best_mae = results.filter(mae__isnull=False).order_by('mae').values_list('id', flat=True).first()

    return render(request, 'dashboard/performance.html', {
        'results': results,
        'datasets': datasets,
        'algorithms': algorithms,
        'dataset_filter': dataset_filter,
        'algo_filter': algo_filter,
        'task_filter': task_filter,
        'best_accuracy_id': best_accuracy,
        'best_f1_id': best_f1,
        'best_rmse_id': best_rmse,
        'best_mae_id': best_mae,
        'task_choices': Dataset.TASK_CHOICES,
    })


@login_required
def results_detail(request, pk):
    result = get_object_or_404(TrainingResult, pk=pk)
    return render(request, 'dashboard/result_detail.html', {'result': result})


@login_required
@user_passes_test(is_admin)
def benchmark_schedule(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        dataset_ids = request.POST.getlist('datasets')
        algo_ids = request.POST.getlist('algorithms')

        if not name:
            messages.error(request, 'Please provide a job name.')
        elif not dataset_ids:
            messages.error(request, 'Please select at least one dataset.')
        elif not algo_ids:
            messages.error(request, 'Please select at least one algorithm.')
        else:
            job = BenchmarkJob.objects.create(name=name, scheduled_by=request.user)
            job.datasets.set(dataset_ids)
            job.algorithms.set(algo_ids)
            log_action(request.user, 'SCHEDULE_BENCHMARK', f'Scheduled: {name}', request)
            messages.success(request, f'Benchmark job "{name}" scheduled with {len(dataset_ids)} datasets × {len(algo_ids)} algorithms.')
            return redirect('dashboard:benchmark_monitor')

    datasets = Dataset.objects.filter(status='active')
    algorithms = AlgorithmConfig.objects.filter(status='enabled')
    return render(request, 'dashboard/benchmark_schedule.html', {
        'datasets': datasets,
        'algorithms': algorithms,
    })


@login_required
@user_passes_test(is_admin)
def benchmark_monitor(request):
    jobs = BenchmarkJob.objects.select_related('scheduled_by').order_by('-created_at')
    return render(request, 'dashboard/benchmark_monitor.html', {'jobs': jobs})


@login_required
@user_passes_test(is_admin)
def run_benchmark_job(request, pk):
    """Actually execute a benchmark job."""
    job = get_object_or_404(BenchmarkJob, pk=pk)
    if job.status not in ['pending']:
        messages.error(request, f'Job is already {job.status}.')
        return redirect('dashboard:benchmark_monitor')

    job.status = 'running'
    job.started_at = timezone.now()
    job.save()

    success_count = 0
    fail_count = 0

    for dataset in job.datasets.all():
        for algo in job.algorithms.all():
            try:
                target_col = dataset.target_column
                if not target_col:
                    continue
                df = load_dataset(dataset.file.path, dataset.file_format)
                results = train_and_evaluate(
                    df, target_col,
                    algo.algorithm_type,
                    algo.hyperparameters,
                    dataset.task_type
                )
                TrainingResult.objects.create(
                    dataset=dataset,
                    algorithm_config=algo,
                    user=request.user,
                    rmse=results.get('rmse'),
                    mae=results.get('mae'),
                    accuracy=results.get('accuracy'),
                    f1_score=results.get('f1_score'),
                    r2_score=results.get('r2_score'),
                    cv_scores=results.get('cv_scores', []),
                    training_time=results.get('training_time'),
                    status='completed',
                )
                success_count += 1
            except Exception as e:
                TrainingResult.objects.create(
                    dataset=dataset,
                    algorithm_config=algo,
                    user=request.user,
                    status='failed',
                    error_message=str(e)
                )
                fail_count += 1

    job.status = 'completed'
    job.completed_at = timezone.now()
    job.save()

    log_action(request.user, 'RUN_BENCHMARK',
               f'Job "{job.name}": {success_count} success, {fail_count} failed', request)
    messages.success(request, f'Benchmark complete: {success_count} succeeded, {fail_count} failed.')
    return redirect('dashboard:benchmark_monitor')


@login_required
@user_passes_test(is_admin)
def cancel_job(request, pk):
    job = get_object_or_404(BenchmarkJob, pk=pk)
    if job.status in ['pending', 'running']:
        job.status = 'cancelled'
        job.save()
        log_action(request.user, 'CANCEL_BENCHMARK', f'Cancelled: {job.name}', request)
        messages.warning(request, f'Job "{job.name}" cancelled.')
    return redirect('dashboard:benchmark_monitor')


@login_required
def api_results(request):
    results = TrainingResult.objects.filter(
        status='completed'
    ).select_related('algorithm_config', 'dataset')
    data = [{
        'id': r.id,
        'algorithm': r.algorithm_config.name,
        'dataset': r.dataset.name,
        'task_type': r.dataset.task_type,
        'rmse': r.rmse,
        'mae': r.mae,
        'accuracy': r.accuracy,
        'f1_score': r.f1_score,
        'r2_score': r.r2_score,
        'training_time': r.training_time,
        'cv_scores': r.cv_scores,
        'date': r.created_at.strftime('%Y-%m-%d'),
    } for r in results]
    return JsonResponse({'results': data})