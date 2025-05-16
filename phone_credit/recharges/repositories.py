

from credits.repositories import CreditRepository
from transactions.models import TransactionLog
from django.db import transaction
from django.db.models import F

from transactions.repositories import TransactionRepository
from .models import PhoneNumber



class RechargeProcessRepository:

    @staticmethod
    def increase_phone_number_charge(amount,phone_number):
        phone_number = (
            PhoneNumber.objects.select_for_update()
            .get(number=phone_number)
        )
        phone_number.credit = F('credit') + amount
        phone_number.save()

        return phone_number


    @staticmethod
    def selling_charge_to_phone_number(user,amount,phone_number):
        with transaction.atomic():
            try:
                CreditRepository.decrease_credit(user=user,amount=amount)
                TransactionRepository.create_new_transaction(
                    amount=amount,
                    type_=TransactionLog.CREDIT,
                    seller=user,
                    action_type=TransactionLog.DECREASE,
                    description=f"Decrease Credit for seller: {user} for {amount} Toman"
                )
                increase_user_phone_charge=RechargeProcessRepository.increase_phone_number_charge(amount,phone_number)
                if increase_user_phone_charge:
                    TransactionRepository.create_new_transaction(
                        amount=amount,
                        type_=TransactionLog.RECHARGE,
                        seller=user,
                        action_type=TransactionLog.INCREASE,
                        description=f"INCREASE Credit for phone number: {phone_number} for {amount} Toman"
                        )
                    return increase_user_phone_charge
            
            except Exception as e:
                raise ValueError(f"There was a problem for selling charge to user: {user.username} credit. {e}")
            