# recharges/models.py

from django.db import models
from django.conf import settings
from transactions.models import TransactionLog

class PhoneNumber(models.Model):
    number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.number

class Recharge(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'is_seller': True})
    phone_number = models.ForeignKey(PhoneNumber, on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def apply(self):
        from django.db import transaction

        with transaction.atomic():
            # Lock seller’s transaction logs
            total_credit = TransactionLog.objects.select_for_update().filter(
                seller=self.seller
            ).aggregate(total=models.Sum('amount'))['total'] or 0

            if total_credit < self.amount:
                raise ValueError("Insufficient credit")

            # Save recharge log
            self.save()

            TransactionLog.objects.create(
                seller=self.seller,
                type=TransactionLog.RECHARGE,
                amount=-self.amount,
                description=f"Recharge for {self.phone_number}"
            )
