# transactions/models.py

from django.db import models
from django.conf import settings

from accounts.models import User

class TransactionLog(models.Model):
    CREDIT = 'credit'
    RECHARGE = 'recharge'
    INCREASE = 'increase'
    DECREASE = 'decrease'

    TYPE_CHOICES = [
        (CREDIT, 'Credit'),
        (RECHARGE, 'Recharge'),
    ]
    ACTION_TYPE_CHOICE = [
        (DECREASE, 'Decrease'),
        (INCREASE, 'Increase'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_seller': True})
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    action_type = models.CharField(max_length=20, choices=ACTION_TYPE_CHOICE)
    amount = models.BigIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
