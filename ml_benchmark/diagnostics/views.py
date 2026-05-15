import os
import uuid
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .models import DiagnosticReport
from .utils import compute_vif, compute_correlation_matrix, generate_heatmap
from datasets.models import Dataset
from datasets.utils import load_dataset
from accounts.views import log_action

@login_required
def run_diagnostic(request):
    datasets = Dataset.objects.filter(status='active')
    if request.method == 'POST':
        dataset_id = request.POST.get('dataset_id')
        vif_threshold = float(request.POST.get('vif_threshold', 5.0))
        dataset = get_object_or_404(Dataset, pk=dataset_id)

        try:
            df = load_dataset(dataset.file.path, dataset.file_format)
            target_col = dataset.target_column or ''

            vif_results = compute_vif(df, target_col)
            high_vif = [feat for feat, val in vif_results.items() if val and val > vif_threshold]
            corr_matrix = compute_correlation_matrix(df, target_col)

            # Generate heatmap
            heatmap_dir = os.path.join(settings.MEDIA_ROOT, 'diagnostics')
            os.makedirs(heatmap_dir, exist_ok=True)
            heatmap_filename = f'heatmap_{uuid.uuid4().hex}.png'
            heatmap_path = os.path.join(heatmap_dir, heatmap_filename)
            generate_heatmap(df, target_col, heatmap_path)

            report = DiagnosticReport.objects.create(
                dataset=dataset,
                user=request.user,
                vif_results=vif_results,
                high_vif_features=high_vif,
                vif_threshold=vif_threshold,
                correlation_matrix=corr_matrix,
                heatmap_image=f'diagnostics/{heatmap_filename}',
            )

            log_action(request.user, 'RUN_DIAGNOSTIC', f'Diagnostics on {dataset.name}', request)
            messages.success(request, 'Multicollinearity diagnostic completed.')
            return redirect('diagnostics:report_detail', pk=report.pk)

        except Exception as e:
            messages.error(request, f'Diagnostic failed: {str(e)}')

    return render(request, 'diagnostics/run_diagnostic.html', {'datasets': datasets})

@login_required
def report_detail(request, pk):
    report = get_object_or_404(DiagnosticReport, pk=pk)
    vif_sorted = sorted(report.vif_results.items(), key=lambda x: (x[1] or 0), reverse=True)
    return render(request, 'diagnostics/report_detail.html', {
        'report': report,
        'vif_sorted': vif_sorted,
    })

@login_required
def report_list(request):
    reports = DiagnosticReport.objects.filter(user=request.user).select_related('dataset')
    return render(request, 'diagnostics/report_list.html', {'reports': reports})