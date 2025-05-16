# credits/models.py

from django.db import models
from django.conf import settings
from accounts.models import User
from transactions.models import TransactionLog
    
class CreditRequest(models.Model):
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]

    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_seller': True})
    amount = models.PositiveBigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    def approve(self):
        from django.db import transaction
        from django.utils.timezone import now

        if self.status != self.PENDING:
            return  # Idempotent behavior

        with transaction.atomic():
            self.status = self.APPROVED
            self.approved_at = now()
            self.save()

            # Log the transaction
            TransactionLog.objects.create(
                seller=self.seller,
                type=TransactionLog.CREDIT,
                amount=self.amount,
                description=f"Credit approved (request #{self.pk})"
            )
