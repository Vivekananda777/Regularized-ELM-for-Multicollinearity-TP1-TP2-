import pandas as pd
import numpy as np
import os

os.makedirs('sample_datasets', exist_ok=True)
np.random.seed(42)
n = 500

# Dataset 1 - Loan Approval (Classification)
credit = np.random.randint(300, 850, n)
income = np.random.randint(20000, 120000, n)
debt   = np.round(np.random.uniform(0.1, 0.9, n), 2)
approved = ((credit > 600) & (debt < 0.5) & (income > 40000)).astype(int)

pd.DataFrame({
    'age': np.random.randint(21, 65, n),
    'income': income,
    'credit_score': credit,
    'loan_amount': np.random.randint(5000, 50000, n),
    'employment_years': np.random.randint(0, 30, n),
    'debt_ratio': debt,
    'num_dependents': np.random.randint(0, 5, n),
    'has_mortgage': np.random.choice([0, 1], n),
    'loan_approved': approved
}).to_csv('sample_datasets/loan_approval.csv', index=False)
print("Created: loan_approval.csv")

# Dataset 2 - House Prices (Regression)
sqft  = np.random.randint(500, 4500, n)
beds  = np.random.randint(1, 6, n)
baths = np.random.randint(1, 4, n)
age   = np.random.randint(0, 50, n)
price = (sqft*120 + beds*8000 + baths*5000 - age*500 + np.random.normal(0,15000,n)).astype(int)

pd.DataFrame({
    'sqft': sqft,
    'bedrooms': beds,
    'bathrooms': baths,
    'age_years': age,
    'garage_spaces': np.random.randint(0, 3, n),
    'school_rating': np.round(np.random.uniform(1, 10, n), 1),
    'distance_to_city': np.round(np.random.uniform(0.5, 50, n), 1),
    'has_pool': np.random.choice([0, 1], n, p=[0.8, 0.2]),
    'price': np.clip(price, 50000, 900000)
}).to_csv('sample_datasets/house_prices.csv', index=False)
print("Created: house_prices.csv")

# Dataset 3 - Student Performance (Classification)
study = np.round(np.random.uniform(0, 10, n), 1)
attend = np.random.randint(50, 100, n)
prev  = np.random.randint(40, 100, n)
passed = ((study > 4) & (attend > 70) & (prev > 55)).astype(int)

pd.DataFrame({
    'study_hours': study,
    'attendance': attend,
    'previous_score': prev,
    'sleep_hours': np.round(np.random.uniform(4, 10, n), 1),
    'tutoring': np.random.choice([0, 1], n),
    'internet_access': np.random.choice([0, 1], n),
    'passed': passed
}).to_csv('sample_datasets/student_performance.csv', index=False)
print("Created: student_performance.csv")

print("\nAll datasets created in sample_datasets/ folder!")