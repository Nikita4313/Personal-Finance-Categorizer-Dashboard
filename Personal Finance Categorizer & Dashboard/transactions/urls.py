from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("upload/", views.upload_statement, name="upload_statement"),
    path("chart/<str:chart_type>/", views.chart, name="chart"),
]
