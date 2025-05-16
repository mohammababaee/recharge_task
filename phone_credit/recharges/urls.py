# recharge/urls.py

from django.urls import path
from .views import RechargeView


urlpatterns = [
    path("charge-number/", RechargeView.as_view(), name="credit-request"),
]
