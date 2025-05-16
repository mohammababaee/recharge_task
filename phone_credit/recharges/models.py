# recharges/models.py

from django.db import models
from django.conf import settings
from accounts.models import User
from transactions.models import TransactionLog

class PhoneNumber(models.Model):
    number = models.CharField(max_length=20, unique=True)
    credit = models.PositiveBigIntegerField()

    def __str__(self):
        return self.number

class Recharge(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_seller': True})
    phone_number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    
