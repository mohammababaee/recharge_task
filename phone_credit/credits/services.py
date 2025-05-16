from transactions.models import TransactionLog
from transactions.repositories import TransactionRepository
from .repositories import CreditRepository

class CreditService:
    @staticmethod
    def increase_credit(user,amount):
        credit_response = CreditRepository.increase_credit(user=user,amount=amount,return_updated=True)
        if credit_response:
            TransactionRepository.create_new_transaction(
                amount=amount,
                type_=TransactionLog.RECHARGE,
                seller=user,
                description=f"Increase Credit request for user: {user} for {amount} Toman"
            )
            return credit_response
        else:
            raise ValueError(f"No SellerCredit record found for user {user.username}")