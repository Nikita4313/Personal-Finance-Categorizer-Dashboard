# Ledgerline: Personal Finance Categorizer

A small Django dashboard that imports bank statement CSV files, categorizes transactions with deterministic rules plus a Scikit-learn fallback, stores the results in SQLite, and renders monthly spending charts with Matplotlib.

## Features

- Upload CSV files with exactly these required columns: `date`, `description`, `amount`.
- Keyword rules run first. For example, `SWIGGY` becomes `Food`.
- Unmatched descriptions use a TF-IDF + Logistic Regression model trained from `data/synthetic_training_data.csv`.
- Imported transactions are persisted in `db.sqlite3`.
- Dashboard shows this month's spending, a category bar chart, a category pie chart, and the complete ledger.
- `data/sample_bank_statement.csv` is ready for an immediate test upload.

## Run locally

```powershell
cd path\to\xyz
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`, choose `data/sample_bank_statement.csv`, and select **Import statement**.

Run the automated tests with:

```powershell
python manage.py test
```

## Project structure

- `finance_project/`: Django settings and URL configuration.
- `transactions/models.py`: SQLite-backed transaction model.
- `transactions/services.py`: rule matching and Scikit-learn categorizer.
- `transactions/views.py`: upload, dashboard, and Matplotlib image endpoints.
- `templates/transactions/dashboard.html`: dashboard UI.
- `transactions/static/transactions/styles.css`: responsive visual styling.
- `data/synthetic_training_data.csv`: clearly labeled synthetic training examples, not real financial data.
- `data/sample_bank_statement.csv`: sample input for testing.
- `transactions/tests.py`: upload, categorization, persistence, dashboard, and chart checks.

## Important review note

This is a complete learning project, but it still needs your review and understanding before you claim it as fully self-built on a resume. In particular, review the CSV validation, negative/positive amount convention, model limitations, privacy implications, and chart behavior. The classifier is trained on synthetic examples and should not be treated as financial advice or as production-grade bank reconciliation software.
