
# 🚀 Novel Statistical Regularized Extreme Learning Machine (TP1-ELM & TP2-ELM)

A professional web-based machine learning benchmarking and research platform built with Django, MySQL, Bootstrap 5, and scikit-learn. It allows researchers and analysts to upload datasets, configure ML algorithms, run experiments, analyze multicollinearity, and export detailed PDF reports — all from a single unified interface.

---

## 🔍 Overview

This project presents a novel machine learning approach to address multicollinearity, a common issue where highly correlated features degrade model performance and stability.

To solve this, I developed two advanced algorithms:

TP1-ELM (Two-Parameter Extreme Learning Machine)
TP2-ELM (Two-Parameter Extreme Learning Machine)

These models integrate statistical regularization techniques into the Extreme Learning Machine framework, improving generalization and prediction stability.
The project is implemented as a full-stack MLOps platform using Django, enabling dataset management, diagnostics, model training, benchmarking, and reporting.

---


## 🎯 Problem Statement

Multicollinearity negatively impacts machine learning models by:

Producing unstable coefficients
Reducing interpretability
Causing overfitting and poor generalization

Traditional algorithms do not explicitly handle this issue.

## 💡 Proposed Solution

This project introduces statistical regularization into ELM using:

Ridge Regression (controls coefficient magnitude)
Liu Estimator (controls bias and variance)
## 🔥 Key Innovation
Developed TP1-ELM and TP2-ELM
Combines ridge and Liu estimators into ELM
Improves stability in multicollinear environments


## 🏗️ System Architecture
``
Dataset Upload
      ↓
Data Preprocessing
      ↓
Multicollinearity Detection (VIF + Correlation)
      ↓
TP1-ELM / TP2-ELM Training
      ↓
Performance Evaluation
      ↓
Dashboard & Visualization
      ↓
Report Generation
      ↓
Monitoring System
``

## ✅ Features

### 📊 Data Processing
Dataset upload (CSV, Excel, JSON)
Missing value handling (median/mode)
Feature encoding & normalization
Automated preprocessing reports

### 🔍 Multicollinearity Diagnostics
Variance Inflation Factor (VIF) analysis
Correlation matrix
Heatmap visualization

### 🧠 Machine Learning
Implementation of ELM
TP1-ELM & TP2-ELM algorithms
Support for regression & classification
Hyperparameter configuration

### 📈 Benchmarking
Compare multiple algorithms across datasets
Cross-validation for reliable evaluation
Metrics:
Accuracy, F1-score
RMSE, MAE, R²

### 📊 Dashboard & Visualization
Performance comparison charts
Best model identification
Dataset & algorithm analytics

### 📄 Reporting
Export results as PDF reports
Generate performance charts (PNG/SVG)

### 🛠️ Monitoring
Database health check
Storage monitoring
Module status tracking
Alert system


## 🧪 Benchmarking Strategy

Same dataset used for all models
Identical preprocessing pipeline
Standard evaluation metrics
Cross-validation for robustness
---

## 🛠 Tech Stack

| Layer             | Technology                          |
|-------------------|-------------------------------------|
| Backend           | Python 3.11.9, Django 4.2.7         |
| Database          | MySQL 8.0                           |
| Frontend          | HTML5, CSS3, Bootstrap 5.3, JS      |
| ML Library        | scikit-learn 1.3.2                  |
| Data Processing   | pandas 2.1.3, NumPy 1.26.2          |
| Visualization     | matplotlib 3.8.2, seaborn 0.13.0    |
| PDF Generation    | ReportLab 4.0.7                     |
| Statistics        | statsmodels 0.14.0                  |
| Icons & Fonts     | Font Awesome 6.5, Google Inter      |

---

## 📁 Project Structure

```
ml_benchmark/
│
├── ml_benchmark/               # Project settings and URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                   # User auth, roles, audit log
│   ├── models.py               # CustomUser, AuditLog
│   ├── views.py                # login, register, user management
│   ├── forms.py                # LoginForm, RegisterForm
│   └── urls.py
│
├── datasets/                   # Dataset upload and preprocessing
│   ├── models.py               # Dataset, PreprocessingReport
│   ├── views.py                # upload, list, detail, new_experiment
│   ├── utils.py                # load_dataset, preprocess_dataset
│   └── urls.py
│
├── algorithms/                 # Algorithm config and training
│   ├── models.py               # AlgorithmConfig, TrainingResult
│   ├── views.py                # create, edit, train, saved configs
│   ├── forms.py                # AlgorithmConfigForm
│   ├── utils.py                # train_and_evaluate
│   └── urls.py
│
├── diagnostics/                # VIF and correlation analysis
│   ├── models.py               # DiagnosticReport
│   ├── views.py                # run_diagnostic, report_detail
│   ├── utils.py                # compute_vif, generate_heatmap
│   └── urls.py
│
├── dashboard/                  # Performance dashboard
│   ├── models.py               # BenchmarkJob
│   ├── views.py                # home, performance, results_detail
│   ├── templatetags/
│   │   └── dashboard_extras.py
│   └── urls.py
│
├── exports/                    # PDF and plot export
│   ├── views.py                # export_results_pdf, export_plot_png
│   └── urls.py
│
├── monitoring/                 # System health monitoring
│   ├── models.py               # ModuleHealth, SystemAlert
│   ├── views.py
│   ├── utils.py
│   └── urls.py
│
├── templates/                  # All HTML templates
│   ├── base.html
│   ├── accounts/
│   ├── datasets/
│   ├── algorithms/
│   ├── diagnostics/
│   ├── dashboard/
│   └── monitoring/
│
├── static/
│   ├── css/main.css
│   └── js/main.js
│
├── media/                      # Uploaded files
├── sample_datasets/            # Generated CSV files for testing
├── generate_datasets.py        # Script to create sample data
└── manage.py
```

---

## ⚙️ Installation

### Step 1 — Navigate to project folder

```bash
cd G:\Projects\Novel Statistical Regularized Extreme
```

### Step 2 — Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3 — Install all dependencies

```bash
pip install django==4.2.7
pip install mysqlclient==2.2.0
pip install pandas==2.1.3
pip install numpy==1.26.2
pip install scikit-learn==1.3.2
pip install matplotlib==3.8.2
pip install seaborn==0.13.0
pip install openpyxl==3.1.2
pip install reportlab==4.0.7
pip install statsmodels==0.14.0
pip install Pillow==10.1.0
pip install django-crispy-forms==2.1
pip install crispy-bootstrap5==0.7
pip install whitenoise==6.6.0
```

---

## 🗄️ Database Setup

Open **MySQL Workbench** and run the following SQL:

```sql
CREATE DATABASE ml_benchmark_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ml_user'@'localhost' IDENTIFIED BY 'ml_password123';
GRANT ALL PRIVILEGES ON ml_benchmark_db.* TO 'ml_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## 🚀 Running the Project

Open terminal and run these commands every time you want to start:

```bash
cd G:\Projects\Novel Statistical Regularized Extreme\ml_benchmark

venv\Scripts\activate

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open your browser and go to:

```
http://127.0.0.1:8000/
```

> ⚠️ Keep the terminal open while using the project. The server stops if you close it.

---

## 📊 Sample Datasets

Generate ready-to-use CSV files for testing:

```bash
python generate_datasets.py
```

Files created in `sample_datasets/` folder:

| File                  | Task           | Target Column  | Rows |
|-----------------------|----------------|----------------|------|
| loan_approval.csv     | Classification | loan_approved  | 300  |
| house_prices.csv      | Regression     | price          | 300  |
| student_pass.csv      | Classification | passed         | 300  |
| diabetes.csv          | Classification | diabetic       | 300  |
| salary.csv            | Regression     | salary         | 300  |

---

## 📖 How to Use

### 1. Register or Login
- Go to `http://127.0.0.1:8000/accounts/login/`
- New users can register at `http://127.0.0.1:8000/accounts/register/`
- Superuser created via `python manage.py createsuperuser` gets Admin role automatically

### 2. Run Your First Experiment
- Click **New Experiment** in the sidebar
- **Step 1** — Upload a CSV file and fill dataset details
- **Step 2** — Select algorithm type and configure hyperparameters
- **Step 3** — Click **Run Experiment**
- Results page opens automatically with all metrics

### 3. View Performance Dashboard
- Click **Performance** in the sidebar
- Color-coded table: 👑 Crown = best value, green = good, red = poor
- Filter by dataset, algorithm, or task type
- Export PNG/SVG plots per result

### 4. Run Diagnostics
- Click **Run Diagnostic** in the sidebar
- Select dataset and set VIF threshold (default: 5.0)
- View VIF scores per feature
- View correlation heatmap
- Download diagnostic PDF

### 5. Export Full Report
- Click **Export Report** in the sidebar
- Downloads complete PDF with:
  - All experiment results table
  - Performance charts
  - Cross-validation stability analysis

---

## 👥 User Roles

| Role    | What They Can Do |
|---------|-----------------|
| **User**  | Run experiments, view results, diagnostics, export reports, manage own profile |
| **Admin** | Everything above + manage all users, upload datasets, create algorithm configs, view audit log |

### Creating an Admin
```bash
python manage.py createsuperuser
```
The superuser automatically gets the **Admin** role.

### Upgrading a User to Admin
1. Login as admin
2. Go to **Users** in sidebar
3. Click Edit on the user
4. Change Role to **Admin**
5. Save

---

## 🤖 Algorithms Supported

| Algorithm              | Type        | Key Hyperparameters           |
|------------------------|-------------|-------------------------------|
| Linear Regression      | Regression  | None                          |
| Ridge Regression       | Regression  | alpha (λ)                     |
| Lasso Regression       | Regression  | alpha (λ)                     |
| Random Forest          | Both        | n_estimators, max_depth       |
| Gradient Boosting      | Both        | n_estimators, learning_rate   |
| Support Vector Machine | Both        | C, kernel                     |
| Neural Network (MLP)   | Both        | hidden_layers, max_iter       |
| Decision Tree          | Both        | max_depth                     |
| K-Nearest Neighbors    | Both        | n_neighbors                   |
| Naive Bayes            | Classification | None                       |

All algorithms automatically use:
- **80% training / 20% testing split**
- **5-fold cross-validation**
- Metrics: RMSE, MAE, R² (regression) | Accuracy, F1-Score (classification)

---

## 📋 Functional Requirements Coverage

| ID     | Requirement                                      | Status |
|--------|--------------------------------------------------|--------|
| UFR-01 | Dataset upload with auto preprocessing report    | ✅ Done |
| UFR-02 | Algorithm config with hyperparameter validation  | ✅ Done |
| UFR-03 | VIF multicollinearity diagnostic with heatmap    | ✅ Done |
| UFR-04 | Color-coded performance comparison dashboard     | ✅ Done |
| UFR-05 | PNG, SVG, PDF export for plots and reports       | ✅ Done |
| AFR-01 | Dataset registry with versioning and deprecation | ✅ Done |
| AFR-02 | Algorithm enable/disable toggle by admin         | ✅ Done |
| AFR-03 | Benchmark job scheduling and execution           | ✅ Done |
| AFR-04 | Role-based access control (User / Admin)         | ✅ Done |
| AFR-05 | System health monitoring with alerts             | ✅ Done |

---

## 🔗 Key URLs

| Page                  | URL                                          |
|-----------------------|----------------------------------------------|
| Login                 | http://127.0.0.1:8000/accounts/login/        |
| Register              | http://127.0.0.1:8000/accounts/register/     |
| Dashboard             | http://127.0.0.1:8000/dashboard/             |
| New Experiment        | http://127.0.0.1:8000/datasets/experiment/new/ |
| Datasets              | http://127.0.0.1:8000/datasets/              |
| Algorithms            | http://127.0.0.1:8000/algorithms/            |
| Performance           | http://127.0.0.1:8000/dashboard/performance/ |
| Run Diagnostic        | http://127.0.0.1:8000/diagnostics/run/       |
| Export Report (PDF)   | http://127.0.0.1:8000/exports/results/pdf/   |
| User Management       | http://127.0.0.1:8000/accounts/users/        |
| Audit Log             | http://127.0.0.1:8000/accounts/audit-log/    |

---

## 📝 Notes

- Python version required: **3.11.9**
- MySQL version required: **8.0+**
- Always activate virtual environment before running the server
- Media files (uploaded datasets, heatmap images) are stored in the `media/` folder
- Static files are served by WhiteNoise in development mode

---

## 👩‍💻 Developer

Vivekananda Survi
Machine Learning & Data Engineering Enthusiast
```
