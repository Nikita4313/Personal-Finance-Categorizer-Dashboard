from pathlib import Path

import pandas as pd
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


RULES = {
    "food": "Food",
    "swiggy": "Food",
    "zomato": "Food",
    "restaurant": "Food",
    "grocery": "Groceries",
    "supermarket": "Groceries",
    "bigbasket": "Groceries",
    "uber": "Transport",
    "ola": "Transport",
    "metro": "Transport",
    "fuel": "Transport",
    "petrol": "Transport",
    "rent": "Rent",
    "electricity": "Bills & Utilities",
    "internet": "Bills & Utilities",
    "mobile": "Bills & Utilities",
    "netflix": "Entertainment",
    "cinema": "Entertainment",
    "spotify": "Entertainment",
    "amazon": "Shopping",
    "flipkart": "Shopping",
    "shopping": "Shopping",
    "salary": "Income",
}


class TransactionCategorizer:
    def __init__(self):
        dataset_path = Path(settings.BASE_DIR) / "data" / "synthetic_training_data.csv"
        training_data = pd.read_csv(dataset_path)
        self.model = Pipeline([
            ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000)),
        ])
        self.model.fit(training_data["description"], training_data["category"])

    def categorize(self, description):
        normalized = description.lower()
        for keyword, category in RULES.items():
            if keyword in normalized:
                return category, "rule"
        return str(self.model.predict([description])[0]), "ml"
