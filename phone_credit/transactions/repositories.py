# transactions/repositories/transaction_repository.py

from django.utils.timezone import now
from transactions.models import TransactionLog


class TransactionRepository:
    @staticmethod
    def create_new_transaction(amount, type_, seller, action_type, description=""):
        return TransactionLog.objects.create(
            amount=amount,
            type=type_,
            seller=seller,
            description=description,
            action_type=action_type,
            created_at=now()  # optional, see note below
        )
