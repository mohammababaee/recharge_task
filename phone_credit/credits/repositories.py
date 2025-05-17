from django.db import transaction
from django.db.models import F
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ValidationError

from .models import CreditRequest
from credits.models import SellerCredit
from django.db import transaction
from django.utils.timezone import now

class CreditRepository:

    @staticmethod
    @transaction.atomic
    def decrease_credit(user, amount):
        seller_credit = (
            SellerCredit.objects.select_for_update()
            .get(seller=user)
        )
        seller_credit.refresh_from_db()

        if seller_credit.credit < int(amount):
            print(seller_credit.credit)
            print(amount)
            raise ValidationError("Insufficient credit.")

        seller_credit.credit = F('credit') - int(amount)
        seller_credit.save()

        return True
    
    @staticmethod
    @transaction.atomic
    def increase_credit(user, amount, return_updated=False):
        credit_request = CreditRequest.objects.create(seller=user, amount=amount)

        try:
            seller_credit = (
                SellerCredit.objects.select_for_update()
                .get(seller=user)
            )
        except ObjectDoesNotExist:
            seller_credit = SellerCredit.objects.create(seller=user)
        
        seller_credit.freezed_credit = F('freezed_credit') + amount
        seller_credit.save()

        if return_updated:
            return credit_request

        return True
    
    @staticmethod
    def approve_credit_request(request_id):
        
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