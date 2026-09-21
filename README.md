# AAPL HR Portal (Django)

A real login-based HR portal:
- **Employees** log in and see only their own profile — employment details, personal info, and a salary-slip section (empty until HR adds slips).
- **HR** (staff accounts) get a searchable/filterable roster. Clicking any employee opens their **full** record, including statutory and bank details.
- First login for every account uses the **Employee ID as the password**, and the app forces a password change before anything else is accessible.

## Project structure

```
hr_portal/
├── manage.py
├── requirements.txt
├── .env.example            → copy to .env for production config
├── Procfile                 → for PaaS deploys (Render/Railway/Heroku-style)
├── data/
│   └── employees_full.json  → your real employee data, used only for import (do not commit to git)
├── hr_portal/                → project settings/urls
└── employees/                 → the app: models, views, templates, admin
```

## 1. Run it locally

```bash
cd hr_portal
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser     # for full Django admin access

# Import all 61 employees + create their login accounts.
# Mark specific employee IDs as HR (staff) with --hr:
python manage.py import_employees data/employees_full.json --hr AAPL100

python manage.py runserver
```

Open `http://127.0.0.1:8000/`.
- Log in as any employee: **username = their Employee ID, password = their Employee ID.** You'll be forced to set a new password immediately.
- Log in as the account(s) you passed to `--hr` to see the HR dashboard instead.
- Log in at `/admin/` with the superuser you created to manage everything directly, including adding salary slips.

## 2. Add salary slips

For now, add them through Django Admin (`/admin/` → Salary slips → Add), which lets you enter Basic/HRA/Allowances/Deductions (net pay is calculated automatically) and optionally attach a PDF. Once you have real payroll data, tell me its shape and I'll build a bulk-import command for it too, the same way we did for the employee master data.

## 3. Deploying live

This app is written to deploy on any standard Python host (Render, Railway, PythonAnywhere, or your own VPS). Render is the most beginner-friendly free option:

1. Push this project to a GitHub repository (the `.gitignore` already keeps `data/employees_full.json`, `.env`, and `db.sqlite3` out of it).
2. On [render.com](https://render.com), create a **New Web Service**, connect your repo.
3. Build command: `pip install -r requirements.txt`
   Start command: `gunicorn hr_portal.wsgi`
4. Add a **PostgreSQL** database from Render's dashboard — it gives you a `DATABASE_URL`. Add that, plus everything in `.env.example`, as environment variables in Render's dashboard.
5. Set `DJANGO_DEBUG=False` and `DJANGO_ALLOWED_HOSTS` to your Render URL (e.g. `your-app.onrender.com`).
6. After the first deploy, open Render's shell for your service and run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py import_employees data/employees_full.json --hr AAPL100
   ```
   (You'll need to upload `data/employees_full.json` to the server first, e.g. via Render's shell file upload, or temporarily commit it to a private repo just for this step.)

If you'd rather use your existing MySQL database instead of Postgres: uncomment `mysqlclient` in `requirements.txt`, and set `DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/DBNAME` in your environment. Your MySQL server needs to accept remote connections from your hosting provider's IP — most local/Workbench-only setups won't, unless you move it to a managed MySQL host (e.g. PlanetScale, AWS RDS).

## Security notes

- Aadhaar, PAN, bank account, and address fields are visible only to logged-in HR accounts (`is_staff=True`) via the employee-detail page and Django admin — never on the employee's own profile page in a way that's exposed elsewhere, and never in any file meant to be shared externally.
- `data/employees_full.json` contains real PII. It's excluded from git via `.gitignore` — keep it that way, and don't attach it to chat messages, emails, or shared drives casually.
- Default passwords are each employee's ID, which is guessable — the forced password-change step exists specifically to close that gap immediately on first login. Don't disable that middleware.
- Once live, keep `DJANGO_DEBUG=False` and set a real, random `DJANGO_SECRET_KEY` — never reuse the placeholder in `settings.py`.
