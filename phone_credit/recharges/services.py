from credits.repositories import CreditRepository
from transactions.models import TransactionLog
from transactions.repositories import TransactionRepository
from .repositories import RechargeProcessRepository


class RechargePhoneNumberService:

    @staticmethod
    def charge_phone_number(user,amount,phone_number):
        charging_phone_response = RechargeProcessRepository.selling_charge_to_phone_number(user,amount,phone_number)
        if charging_phone_response:
            return charging_phone_response