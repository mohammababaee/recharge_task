# credits/models.py

from django.db import models
from django.conf import settings
from accounts.models import User
from transactions.models import TransactionLog


class SellerCredit(models.Model):
    seller = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    credit = models.BigIntegerField(default=0)
    freezed_credit = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.seller}: credit amount {self.credit}"
    
class CreditRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_seller': True})
    amount = models.PositiveBigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    
    def __str__(self):
        return f"{self.seller}: credit amount {self.amount}"