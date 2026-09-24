from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("date", "description", "amount", "category", "source")
    list_filter = ("category", "source", "date")
    search_fields = ("description",)
