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
                type_=TransactionLog.CREDIT,
                seller=user,
                action_type=TransactionLog.INCREASE,
                description=f"Increase Credit request for user: {user} for {amount} Toman"
            )
            return credit_response
        else:
            raise ValueError(f"No SellerCredit record found for user {user.username}")
        
    @staticmethod   
    def approve_request(request_id):
        credit_response = CreditRepository.approve_credit_request(request_id=request_id)
        if credit_response:
            TransactionRepository.create_new_transaction(
                amount=credit_response.amount,
                type_=TransactionLog.CREDIT,
                seller=credit_response.seller,
                action_type=TransactionLog.INCREASE,
                description=f"Approve credit and move it in user credit for user {credit_response.seller.username}"
            )
            return credit_response
        else:
            raise ValueError(f"Credit request is already approved ")