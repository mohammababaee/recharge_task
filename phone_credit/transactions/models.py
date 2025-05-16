# transactions/models.py

from django.db import models
from django.conf import settings

from accounts.models import User

class TransactionLog(models.Model):
    CREDIT = 'credit'
    RECHARGE = 'recharge'

    TYPE_CHOICES = [
        (CREDIT, 'Credit'),
        (RECHARGE, 'Recharge'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_seller': True})
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.BigIntegerField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
