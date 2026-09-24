from io import BytesIO
from pathlib import Path

from django.test import RequestFactory, TestCase
from django.urls import reverse

from .models import Transaction
from .services import TransactionCategorizer
from .views import chart, dashboard


class FinanceFlowTests(TestCase):
    def test_rules_and_ml_fallback(self):
        categorizer = TransactionCategorizer()
        self.assertEqual(categorizer.categorize("SWIGGY order"), ("Food", "rule"))
        category, source = categorizer.categorize("Unknown organic market")
        self.assertEqual(category, "Groceries")
        self.assertEqual(source, "ml")

    def test_upload_to_dashboard_pipeline(self):
        csv = BytesIO(
            b"date,description,amount\n"
            b"2026-09-02,SWIGGY order,-420.50\n"
            b"2026-09-04,Monthly salary credit,85000\n"
            b"2026-09-05,Unknown organic market,-1250\n"
        )
        csv.name = "statement.csv"
        response = self.client.post(reverse("upload_statement"), {"statement": csv})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("dashboard"))
        self.assertEqual(Transaction.objects.count(), 3)
        self.assertEqual(Transaction.objects.get(description="SWIGGY order").category, "Food")
        self.assertEqual(Transaction.objects.get(description="Unknown organic market").source, "ml")
        request_factory = RequestFactory()
        dashboard_response = dashboard(request_factory.get("/"))
        self.assertEqual(dashboard_response.status_code, 200)
        self.assertIn("₹1670.50".encode(), dashboard_response.content)
        self.assertIn(b"SWIGGY order", dashboard_response.content)
        self.assertEqual(chart(request_factory.get("/"), "bar").status_code, 200)
        self.assertEqual(chart(request_factory.get("/"), "pie").status_code, 200)
