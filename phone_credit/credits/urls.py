# recharge/urls.py

from django.urls import path
from .views import ApproveCreditView, CreditRequestView


urlpatterns = [
    path("increase-request/", CreditRequestView.as_view(), name="credit-request"),
    path("approve-request/", ApproveCreditView.as_view(), name="credit-request"),
]
