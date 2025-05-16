from .models import CreditRequest
from accounts.models import SellerCredit
from django.db.models import F


class CreditRepository:
    
    @staticmethod
    def increase_credit(user, amount, return_updated=False):
        qs = SellerCredit.objects.filter(user=user)

        updated_rows = qs.update(credit_balance=F('credit_balance') + amount)

        if return_updated and updated_rows:
            return SellerCredit.objects.get(user=user)

        return updated_rows