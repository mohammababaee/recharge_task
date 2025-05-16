# recharge/urls.py

from django.urls import path
from .views import CreditRequestView


urlpatterns = [
    path("request/", CreditRequestView.as_view(), name="credit-request"),
]
