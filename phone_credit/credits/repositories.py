from django.db import transaction
from django.db.models import F

from .models import CreditRequest
from credits.models import SellerCredit
from django.db import transaction
from django.utils.timezone import now

class CreditRepository:

    @staticmethod
    @transaction.atomic
    def increase_credit(user, amount, return_updated=False):
        credit = CreditRequest.objects.create(seller=user, amount=amount)

        SellerCredit.objects.get_or_create(seller=user)

        SellerCredit.objects.filter(seller=user).update(freezed_credit=F('freezed_credit') + amount)

        if return_updated:
            return credit

        return True
    
    @staticmethod
    def approve(request_id):
        
        with transaction.atomic():
            try:
                credit_request = CreditRequest.objects.select_for_update().get(id=request_id)
            except CreditRequest.DoesNotExist:
                return
            
            if credit_request.status != CreditRequest.PENDING:
                return 
            seller = SellerCredit.objects.select_for_update().get(seller = credit_request.seller)
            if seller.freezed_credit < credit_request.amount:
                raise ValueError("Insufficient frozen credit")

            seller.freezed_credit -= credit_request.amount
            seller.credit += credit_request.amount
            seller.save()

            credit_request.status = CreditRequest.APPROVED
            credit_request.approved_at = now()
            credit_request.save()

        return credit_request