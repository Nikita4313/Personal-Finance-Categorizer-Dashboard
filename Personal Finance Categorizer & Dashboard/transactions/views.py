from io import BytesIO

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone

from .models import Transaction
from .services import TransactionCategorizer


def dashboard(request):
    today = timezone.localdate()
    month_transactions = Transaction.objects.filter(date__year=today.year, date__month=today.month)
    total_spending = month_transactions.filter(amount__lt=0).aggregate(total=Sum("amount"))["total"] or 0
    category_totals = list(
        month_transactions.filter(amount__lt=0).values("category").annotate(total=Sum("amount")).order_by("category")
    )
    context = {
        "transactions": Transaction.objects.all(),
        "total_spending": abs(total_spending),
        "category_totals": category_totals,
        "transaction_count": Transaction.objects.count(),
        "current_month": today.strftime("%B %Y"),
    }
    return render(request, "transactions/dashboard.html", context)


def upload_statement(request):
    if request.method != "POST":
        return redirect("dashboard")
    uploaded_file = request.FILES.get("statement")
    if not uploaded_file or not uploaded_file.name.lower().endswith(".csv"):
        messages.error(request, "Please upload a CSV file.")
        return redirect("dashboard")
    try:
        dataframe = pd.read_csv(uploaded_file)
        required_columns = {"date", "description", "amount"}
        if not required_columns.issubset(dataframe.columns):
            raise ValueError("CSV must contain date, description, and amount columns.")
        dataframe["date"] = pd.to_datetime(dataframe["date"], errors="raise").dt.date
        dataframe["amount"] = pd.to_numeric(dataframe["amount"], errors="raise")
        categorizer = TransactionCategorizer()
        records = []
        for row in dataframe.itertuples(index=False):
            category, source = categorizer.categorize(str(row.description))
            records.append(Transaction(
                date=row.date, description=str(row.description), amount=row.amount,
                category=category, source=source,
            ))
        Transaction.objects.bulk_create(records)
        messages.success(request, f"Imported and categorized {len(records)} transactions.")
    except (ValueError, TypeError, KeyError) as error:
        messages.error(request, f"Could not import statement: {error}")
    except Exception as error:
        messages.error(request, f"Import failed unexpectedly: {error}")
    return redirect("dashboard")


def chart(request, chart_type):
    today = timezone.localdate()
    totals = Transaction.objects.filter(
        date__year=today.year, date__month=today.month, amount__lt=0,
    ).values("category").annotate(total=Sum("amount")).order_by("category")
    labels = [item["category"] for item in totals]
    values = [abs(float(item["total"])) for item in totals]
    figure, axis = plt.subplots(figsize=(8, 4.5), dpi=120)
    if chart_type == "pie":
        axis.pie(values, labels=labels, autopct="%1.0f%%", startangle=90)
        axis.set_title("Spending by category")
    elif chart_type == "bar":
        axis.bar(labels, values, color="#ef8354")
        axis.set_title("Spending by category")
        axis.set_ylabel("Amount")
        axis.tick_params(axis="x", rotation=25)
    else:
        plt.close(figure)
        return HttpResponse("Unknown chart", status=404)
    figure.tight_layout()
    output = BytesIO()
    figure.savefig(output, format="png", transparent=False, facecolor="#fffaf3")
    plt.close(figure)
    return HttpResponse(output.getvalue(), content_type="image/png")
