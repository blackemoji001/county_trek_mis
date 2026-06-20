# County Trek MIS

Multi-tenant SACCO Transport Management System.

## Windows Setup
1. `python -m venv venv`
2. `venv\Scripts\activate`
3. `pip install -r requirements.txt`
4. Edit `.env` with your PostgreSQL credentials.
5. `python manage.py migrate`
6. `python manage.py createsuperuser`
7. `python manage.py runserver`
