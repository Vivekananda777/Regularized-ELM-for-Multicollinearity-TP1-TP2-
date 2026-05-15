# 1. Activate venv
venv\Scripts\activate

# 2. requirements
pip install -r requirements.txt

# 3. Database Creation
create database ml_benchmark_db;

# 4. Migrate
python manage.py makemigrations
python manage.py migrate

# 5. Generate all data
python generate_data.py

# 6. Run server
python manage.py runserver
