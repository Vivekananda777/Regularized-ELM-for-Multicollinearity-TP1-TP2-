import os
import json
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import Dataset, PreprocessingReport
from .forms import DatasetUploadForm, DatasetFilterForm
from .utils import load_dataset, preprocess_dataset
from accounts.views import log_action, is_admin, can_upload


def role_required(test_func, redirect_url='dashboard:home'):
    from functools import wraps
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not test_func(request.user):
                messages.error(request, 'You do not have permission to perform this action.')
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


@login_required
def dataset_list(request):
    form = DatasetFilterForm(request.GET)
    if request.user.is_admin_user():
        datasets = Dataset.objects.all()
    else:
        datasets = Dataset.objects.filter(status='active')
    if form.is_valid():
        if form.cleaned_data.get('task_type'):
            datasets = datasets.filter(task_type=form.cleaned_data['task_type'])
        if form.cleaned_data.get('domain'):
            datasets = datasets.filter(domain__icontains=form.cleaned_data['domain'])
    stats = {
        'total': datasets.count(),
        'active': datasets.filter(status='active').count(),
        'deprecated': datasets.filter(status='deprecated').count(),
    }
    return render(request, 'datasets/dataset_list.html', {
        'datasets': datasets.order_by('-created_at'),
        'form': form,
        'stats': stats,
    })


@login_required
def dataset_upload(request):
    if not request.user.can_upload():
        messages.error(request, 'Your role does not permit dataset uploads.')
        return redirect('datasets:dataset_list')

    preprocess_steps = [
        ('Missing Value Imputation (median/mode)', '🔧', 'rgba(79,70,229,0.2)'),
        ('Categorical Label Encoding', '🏷️', 'rgba(124,58,237,0.2)'),
        ('Standard Normalization (Z-score)', '📊', 'rgba(6,182,212,0.2)'),
        ('Feature Summary Report Generation', '📋', 'rgba(16,185,129,0.2)'),
    ]

    form = DatasetUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        dataset = form.save(commit=False)
        dataset.uploaded_by = request.user
        file_ext = os.path.splitext(form.cleaned_data['file'].name)[1].lower().strip('.')
        dataset.file_format = file_ext
        dataset.status = 'processing'
        dataset.save()

        try:
            df = load_dataset(dataset.file.path, dataset.file_format)
            target_col = dataset.target_column or ''
            df_processed, report_data = preprocess_dataset(df.copy(), target_col)

            dataset.rows = df_processed.shape[0]
            dataset.columns = df_processed.shape[1]
            dataset.status = 'active'
            dataset.save()

            PreprocessingReport.objects.create(
                dataset=dataset,
                missing_values_handled=report_data['missing_handled'],
                columns_normalized=', '.join(report_data['normalized_cols']),
                columns_encoded=', '.join(report_data['encoded_cols']),
                transformations=report_data['transformations'],
                feature_names=report_data['feature_names'],
                original_rows=report_data['original_rows'],
                original_cols=report_data['original_cols'],
            )

            log_action(request.user, 'UPLOAD_DATASET', f'Uploaded: {dataset.name}', request)
            messages.success(request, f'Dataset "{dataset.name}" uploaded and preprocessed successfully!')
            return redirect('datasets:dataset_detail', pk=dataset.pk)

        except Exception as e:
            dataset.status = 'active'
            dataset.save()
            messages.warning(request, f'Dataset saved but preprocessing had an issue: {str(e)}')
            return redirect('datasets:dataset_list')

    return render(request, 'datasets/dataset_upload.html', {
        'form': form,
        'preprocess_steps': preprocess_steps,
    })


@login_required
def dataset_detail(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    if dataset.status == 'deprecated' and not request.user.is_admin_user():
        messages.error(request, 'This dataset is deprecated.')
        return redirect('datasets:dataset_list')
    report = None
    try:
        report = dataset.preprocessing_report
    except PreprocessingReport.DoesNotExist:
        pass
    return render(request, 'datasets/dataset_detail.html', {
        'dataset': dataset,
        'report': report,
    })


@login_required
@user_passes_test(is_admin)
def dataset_deprecate(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    dataset.status = 'deprecated'
    dataset.save()
    log_action(request.user, 'DEPRECATE_DATASET', f'Deprecated: {dataset.name}', request)
    messages.warning(request, f'Dataset "{dataset.name}" deprecated. Hidden from users but retained for audit.')
    return redirect('datasets:dataset_list')


@login_required
@user_passes_test(is_admin)
def dataset_restore(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    dataset.status = 'active'
    dataset.save()
    log_action(request.user, 'RESTORE_DATASET', f'Restored: {dataset.name}', request)
    messages.success(request, f'Dataset "{dataset.name}" restored to active.')
    return redirect('datasets:dataset_list')


@login_required
def dataset_preview(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    try:
        df = load_dataset(dataset.file.path, dataset.file_format)
        preview = df.head(10).fillna('').to_dict(orient='records')
        columns = list(df.columns)
        dtypes = {col: str(df[col].dtype) for col in columns}
        null_counts = {col: int(df[col].isnull().sum()) for col in columns}
        return JsonResponse({
            'columns': columns,
            'rows': preview,
            'total_rows': len(df),
            'dtypes': dtypes,
            'null_counts': null_counts,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def new_experiment(request):
    """Single unified form: upload dataset + configure algorithm + train."""
    from algorithms.models import AlgorithmConfig, TrainingResult
    from algorithms.utils import train_and_evaluate

    preprocess_steps = [
        ('Missing Value Imputation', '🔧', 'rgba(79,70,229,0.2)'),
        ('Categorical Label Encoding', '🏷️', 'rgba(124,58,237,0.2)'),
        ('Standard Normalization', '📊', 'rgba(6,182,212,0.2)'),
        ('Preprocessing Report', '📋', 'rgba(16,185,129,0.2)'),
    ]

    if request.method == 'POST':
        # ── Step 1: Save dataset ──────────────────────────────────────
        file        = request.FILES.get('file')
        ds_name     = request.POST.get('ds_name', '').strip()
        domain      = request.POST.get('domain', '').strip()
        task_type   = request.POST.get('task_type', '')
        version     = request.POST.get('version', '1.0').strip()
        target_col  = request.POST.get('target_column', '').strip()
        description = request.POST.get('description', '').strip()

        # ── Step 2: Algorithm settings ────────────────────────────────
        algo_name   = request.POST.get('algo_name', '').strip()
        algo_type   = request.POST.get('algo_type', '')
        algo_desc   = request.POST.get('algo_desc', '').strip()

        # Hyperparameters
        hyperparams = {}
        for key in ['alpha', 'n_estimators', 'max_depth', 'learning_rate',
                    'C', 'kernel', 'hidden_layers', 'max_iter', 'n_neighbors']:
            val = request.POST.get(key, '').strip()
            if val:
                try:
                    hyperparams[key] = float(val) if '.' in val else int(val)
                except ValueError:
                    hyperparams[key] = val

        # ── Validate required fields ──────────────────────────────────
        errors = []
        if not file:
            errors.append('Please upload a dataset file.')
        if not ds_name:
            errors.append('Dataset name is required.')
        if not domain:
            errors.append('Domain is required.')
        if not task_type:
            errors.append('Task type is required.')
        if not target_col:
            errors.append('Target column is required.')
        if not algo_name:
            errors.append('Algorithm name is required.')
        if not algo_type:
            errors.append('Algorithm type is required.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'datasets/new_experiment.html', {
                'preprocess_steps': preprocess_steps,
                'post': request.POST,
            })

        try:
            # Save dataset file
            file_ext = os.path.splitext(file.name)[1].lower().strip('.')
            dataset = Dataset.objects.create(
                name=ds_name,
                domain=domain,
                task_type=task_type,
                version=version,
                target_column=target_col,
                description=description,
                file=file,
                file_format=file_ext,
                uploaded_by=request.user,
                status='processing',
            )

            # Preprocess
            df = load_dataset(dataset.file.path, file_ext)
            df_processed, report_data = preprocess_dataset(df.copy(), target_col)

            dataset.rows    = df_processed.shape[0]
            dataset.columns = df_processed.shape[1]
            dataset.status  = 'active'
            dataset.save()

            PreprocessingReport.objects.create(
                dataset=dataset,
                missing_values_handled=report_data['missing_handled'],
                columns_normalized=', '.join(report_data['normalized_cols']),
                columns_encoded=', '.join(report_data['encoded_cols']),
                transformations=report_data['transformations'],
                feature_names=report_data['feature_names'],
                original_rows=report_data['original_rows'],
                original_cols=report_data['original_cols'],
            )

            # Save algorithm config
            algo_config = AlgorithmConfig.objects.create(
                name=algo_name,
                algorithm_type=algo_type,
                description=algo_desc,
                hyperparameters=hyperparams,
                created_by=request.user,
                status='enabled',
            )

            # Train model
            if target_col not in df.columns:
                messages.error(request, f'Column "{target_col}" not found in dataset.')
                return redirect('datasets:new_experiment')

            results = train_and_evaluate(
                df, target_col,
                algo_type,
                hyperparams,
                task_type
            )

            tr = TrainingResult.objects.create(
                dataset=dataset,
                algorithm_config=algo_config,
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

            log_action(request.user, 'NEW_EXPERIMENT',
                       f'{algo_name} on {ds_name}', request)
            messages.success(
                request,
                f'Experiment complete! {algo_name} trained on {ds_name} '
                f'in {results["training_time"]}s.'
            )
            return redirect('dashboard:results_detail', pk=tr.pk)

        except Exception as e:
            messages.error(request, f'Experiment failed: {str(e)}')
            return render(request, 'datasets/new_experiment.html', {
                'preprocess_steps': preprocess_steps,
                'post': request.POST,
            })

    return render(request, 'datasets/new_experiment.html', {
        'preprocess_steps': preprocess_steps,
        'post': {},
    })