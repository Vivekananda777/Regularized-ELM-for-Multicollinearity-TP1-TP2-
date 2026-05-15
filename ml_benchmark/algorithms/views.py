import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from .models import AlgorithmConfig, SavedConfiguration, TrainingResult
from .forms import AlgorithmConfigForm, SavedConfigForm, TrainModelForm
from .utils import train_and_evaluate
from datasets.models import Dataset
from datasets.utils import load_dataset
from accounts.views import log_action, is_admin


@login_required
def algorithm_list(request):
    if request.user.is_admin_user():
        algorithms = AlgorithmConfig.objects.all()
    else:
        algorithms = AlgorithmConfig.objects.filter(status='enabled')
    return render(request, 'algorithms/algorithm_list.html', {'algorithms': algorithms})


@login_required
def algorithm_create(request):
    if not request.user.can_configure():
        messages.error(request, 'You do not have permission to create algorithm configurations.')
        return redirect('algorithms:algorithm_list')
    form = AlgorithmConfigForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        config = form.save(commit=False)
        config.created_by = request.user
        config.save()
        log_action(request.user, 'CREATE_ALGORITHM', f'Created: {config.name}', request)
        messages.success(request, f'Algorithm configuration "{config.name}" created successfully.')
        return redirect('algorithms:algorithm_list')
    return render(request, 'algorithms/algorithm_form.html', {'form': form, 'title': 'New Algorithm Configuration'})


@login_required
def algorithm_edit(request, pk):
    config = get_object_or_404(AlgorithmConfig, pk=pk)
    if not request.user.can_configure():
        messages.error(request, 'You do not have permission to edit configurations.')
        return redirect('algorithms:algorithm_list')
    form = AlgorithmConfigForm(request.POST or None, instance=config)
    if request.method == 'POST' and form.is_valid():
        form.save()
        log_action(request.user, 'EDIT_ALGORITHM', f'Edited: {config.name}', request)
        messages.success(request, f'Configuration "{config.name}" updated.')
        return redirect('algorithms:algorithm_list')
    if config.hyperparameters:
        for key, val in config.hyperparameters.items():
            if key in form.fields:
                form.fields[key].initial = val
    return render(request, 'algorithms/algorithm_form.html', {
        'form': form,
        'title': f'Edit — {config.name}',
        'config': config,
    })


@login_required
@user_passes_test(is_admin)
def algorithm_toggle(request, pk):
    config = get_object_or_404(AlgorithmConfig, pk=pk)
    config.status = 'disabled' if config.status == 'enabled' else 'enabled'
    config.save()
    log_action(request.user, 'TOGGLE_ALGORITHM', f'{config.status}: {config.name}', request)
    messages.info(request, f'Algorithm "{config.name}" is now {config.status}.')
    return redirect('algorithms:algorithm_list')


@login_required
def train_model(request):
    if not request.user.can_train():
        messages.error(request, 'Your role does not permit model training.')
        return redirect('dashboard:home')

    form = TrainModelForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        dataset = form.cleaned_data['dataset']
        algo_config = form.cleaned_data['algorithm']
        target_col = form.cleaned_data.get('target_column') or dataset.target_column

        if not target_col:
            messages.error(request, 'Please specify a target column for training.')
            return render(request, 'algorithms/train_model.html', {'form': form})

        try:
            df = load_dataset(dataset.file.path, dataset.file_format)
            if target_col not in df.columns:
                messages.error(request, f'Column "{target_col}" not found. Available: {", ".join(df.columns[:10])}')
                return render(request, 'algorithms/train_model.html', {'form': form})

            if len(df) < 10:
                messages.error(request, 'Dataset too small. Need at least 10 rows.')
                return render(request, 'algorithms/train_model.html', {'form': form})

            results = train_and_evaluate(
                df, target_col,
                algo_config.algorithm_type,
                algo_config.hyperparameters,
                dataset.task_type
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

            log_action(request.user, 'TRAIN_MODEL',
                       f'{algo_config.name} on {dataset.name} — time:{results["training_time"]}s', request)
            messages.success(request, f'Model trained in {results["training_time"]}s!')
            return redirect('dashboard:results_detail', pk=tr.pk)

        except Exception as e:
            TrainingResult.objects.create(
                dataset=dataset,
                algorithm_config=algo_config,
                user=request.user,
                status='failed',
                error_message=str(e)
            )
            log_action(request.user, 'TRAIN_FAILED', f'{algo_config.name}: {str(e)}', request)
            messages.error(request, f'Training failed: {str(e)}')

    return render(request, 'algorithms/train_model.html', {'form': form})


@login_required
def saved_configs(request):
    configs = SavedConfiguration.objects.filter(user=request.user).select_related('algorithm_config')
    return render(request, 'algorithms/saved_configs.html', {'configs': configs})


@login_required
def save_config(request, algo_pk):
    algo = get_object_or_404(AlgorithmConfig, pk=algo_pk)
    form = SavedConfigForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        sc = form.save(commit=False)
        sc.user = request.user
        sc.algorithm_config = algo
        sc.hyperparameters = algo.hyperparameters
        sc.save()
        log_action(request.user, 'SAVE_CONFIG', f'Saved config: {sc.name}', request)
        messages.success(request, f'Configuration "{sc.name}" saved successfully.')
        return redirect('algorithms:saved_configs')
    return render(request, 'algorithms/save_config_form.html', {'form': form, 'algo': algo})


@login_required
def delete_saved_config(request, pk):
    cfg = get_object_or_404(SavedConfiguration, pk=pk, user=request.user)
    cfg.delete()
    messages.success(request, 'Saved configuration deleted.')
    return redirect('algorithms:saved_configs')


@login_required
def training_history(request):
    results = TrainingResult.objects.filter(user=request.user).select_related('dataset', 'algorithm_config')
    return render(request, 'algorithms/training_history.html', {'results': results})