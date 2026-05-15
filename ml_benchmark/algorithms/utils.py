import numpy as np
import pandas as pd
import time
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, accuracy_score, f1_score, r2_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

def get_model(algorithm_type, hyperparams, task_type):
    """Return sklearn model based on algorithm type and task."""
    is_regression = task_type == 'regression'
    models_map = {
        'linear_regression': LinearRegression(),
        'ridge_regression': Ridge(alpha=hyperparams.get('alpha', 1.0)),
        'lasso_regression': Lasso(alpha=hyperparams.get('alpha', 1.0)),
        'random_forest': RandomForestRegressor(
            n_estimators=int(hyperparams.get('n_estimators', 100)),
            max_depth=hyperparams.get('max_depth') or None,
            random_state=42
        ) if is_regression else RandomForestClassifier(
            n_estimators=int(hyperparams.get('n_estimators', 100)),
            max_depth=hyperparams.get('max_depth') or None,
            random_state=42
        ),
        'gradient_boosting': GradientBoostingRegressor(
            n_estimators=int(hyperparams.get('n_estimators', 100)),
            learning_rate=float(hyperparams.get('learning_rate', 0.1)),
            random_state=42
        ) if is_regression else GradientBoostingClassifier(
            n_estimators=int(hyperparams.get('n_estimators', 100)),
            learning_rate=float(hyperparams.get('learning_rate', 0.1)),
            random_state=42
        ),
        'svm': SVR(C=float(hyperparams.get('C', 1.0)), kernel=hyperparams.get('kernel', 'rbf')
        ) if is_regression else SVC(C=float(hyperparams.get('C', 1.0)), kernel=hyperparams.get('kernel', 'rbf')),
        'neural_network': MLPRegressor(
            hidden_layer_sizes=tuple(int(x) for x in str(hyperparams.get('hidden_layers', '100')).split(',')),
            max_iter=int(hyperparams.get('max_iter', 500)),
            random_state=42
        ) if is_regression else MLPClassifier(
            hidden_layer_sizes=tuple(int(x) for x in str(hyperparams.get('hidden_layers', '100')).split(',')),
            max_iter=int(hyperparams.get('max_iter', 500)),
            random_state=42
        ),
        'decision_tree': DecisionTreeRegressor(
            max_depth=hyperparams.get('max_depth') or None, random_state=42
        ) if is_regression else DecisionTreeClassifier(
            max_depth=hyperparams.get('max_depth') or None, random_state=42
        ),
        'knn': KNeighborsRegressor(n_neighbors=int(hyperparams.get('n_neighbors', 5))
        ) if is_regression else KNeighborsClassifier(n_neighbors=int(hyperparams.get('n_neighbors', 5))),
        'naive_bayes': GaussianNB(),
    }
    return models_map.get(algorithm_type)

def train_and_evaluate(df, target_column, algorithm_type, hyperparams, task_type):
    """Train model and return metrics."""
    df = df.copy()

    # Encode target if classification
    le = None
    if task_type == 'classification' and df[target_column].dtype == 'object':
        le = LabelEncoder()
        df[target_column] = le.fit_transform(df[target_column].astype(str))

    # Drop rows with missing values in target
    df = df.dropna(subset=[target_column])

    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Handle remaining missing values in features
    X = X.fillna(X.mean() if X.select_dtypes(include=np.number).shape[1] > 0 else 0)

    model = get_model(algorithm_type, hyperparams, task_type)
    if model is None:
        raise ValueError(f"Unknown algorithm: {algorithm_type}")

    start_time = time.time()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    training_time = time.time() - start_time

    results = {'training_time': round(training_time, 4)}

    if task_type == 'regression':
        results['rmse'] = round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4)
        results['mae'] = round(float(mean_absolute_error(y_test, y_pred)), 4)
        results['r2_score'] = round(float(r2_score(y_test, y_pred)), 4)
        scoring = 'neg_mean_squared_error'
    else:
        results['accuracy'] = round(float(accuracy_score(y_test, y_pred)), 4)
        results['f1_score'] = round(float(f1_score(y_test, y_pred, average='weighted', zero_division=0)), 4)
        scoring = 'accuracy'

    # Cross-validation
    try:
        cv_scores = cross_val_score(model, X, y, cv=5, scoring=scoring)
        if task_type == 'regression':
            cv_scores = np.sqrt(np.abs(cv_scores))
        results['cv_scores'] = [round(float(s), 4) for s in cv_scores]
    except Exception:
        results['cv_scores'] = []

    return results