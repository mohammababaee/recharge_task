from multiprocessing import Process
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import PhoneNumber, Recharge
from .repositories import RechargeProcessRepository
from credits.models import SellerCredit
from transactions.models import TransactionLog
from django.db import connections

User = get_user_model()

class RechargeModelTests(TestCase):
    def setUp(self):
        # Create test users
        self.seller1 = User.objects.create_user(
            username='seller1',
            password='testpass123',
            is_seller=True
        )
        self.seller2 = User.objects.create_user(
            username='seller2',
            password='testpass123',
            is_seller=True
        )
        
        # Create seller credits
        self.seller1_credit = SellerCredit.objects.create(
            seller=self.seller1,
            credit=1000000  # 1,000,000 Toman
        )
        self.seller2_credit = SellerCredit.objects.create(
            seller=self.seller2,
            credit=1000000  # 1,000,000 Toman
        )
        
        # Create test phone numbers
        self.phone1 = PhoneNumber.objects.create(
            number='+989123456789',
            credit=0
        )
        self.phone2 = PhoneNumber.objects.create(
            number='+989987654321',
            credit=0
        )

    def test_recharge_creation(self):
        """Test basic recharge creation"""
        recharge = Recharge.objects.create(
            seller=self.seller1,
            phone_number=self.phone1,
            amount=50000
        )
        self.assertEqual(recharge.amount, 50000)
        self.assertEqual(recharge.seller, self.seller1)
        self.assertEqual(recharge.phone_number, self.phone1)

    def test_recharge_process(self):
        """Test complete recharge process"""
        initial_seller_credit = self.seller1_credit.credit
        initial_phone_credit = self.phone1.credit
        recharge_amount = 50000

        # Process recharge
        RechargeProcessRepository.selling_charge_to_phone_number(
            user=self.seller1,
            amount=recharge_amount,
            phone_number=self.phone1.number
        )

        # Verify seller credit decrease
        self.seller1_credit.refresh_from_db()
        self.assertEqual(
            self.seller1_credit.credit,
            initial_seller_credit - recharge_amount
        )

        # Verify phone credit increase
        self.phone1.refresh_from_db()
        self.assertEqual(
            self.phone1.credit,
            initial_phone_credit + recharge_amount
        )

    def test_insufficient_credit_recharge(self):
        """Test recharge with insufficient credit"""
        with self.assertRaises(ValueError):
            RechargeProcessRepository.selling_charge_to_phone_number(
                user=self.seller1,
                amount=2000000,  # More than available credit
                phone_number=self.phone1.number
            )

    def test_concurrent_recharges(self):
        """Test concurrent recharge operations"""

        def recharge_operation():
            # You need to re-fetch seller and phone from DB in each process
            seller = User.objects.get(pk=self.seller1.pk)
            phone = PhoneNumber.objects.get(pk=self.phone1.pk)
            with transaction.atomic():
                RechargeProcessRepository.selling_charge_to_phone_number(
                    user=seller,
                    amount=10000,
                    phone_number=phone.number
                )

        # Simulate concurrent recharges using multiprocessing
        processes = []
        for _ in range(10):
            p = Process(target=recharge_operation)
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        self.seller1_credit.refresh_from_db()
        self.phone1.refresh_from_db()

        self.assertEqual(
            self.seller1_credit.credit,
            900000  # 1,000,000 - (10 * 10,000)
        )
        self.assertEqual(
            self.phone1.credit,
            100000  # 0 + (10 * 10,000)
        )
        connections.close_all()

    def test_multiple_sellers_recharge(self):
        """Test recharges from multiple sellers"""
        # First seller recharges
        RechargeProcessRepository.selling_charge_to_phone_number(
            user=self.seller1,
            amount=50000,
            phone_number=self.phone1.number
        )

        # Second seller recharges
        RechargeProcessRepository.selling_charge_to_phone_number(
            user=self.seller2,
            amount=75000,
            phone_number=self.phone1.number
        )

        # Verify final balances
        self.seller1_credit.refresh_from_db()
        self.seller2_credit.refresh_from_db()
        self.phone1.refresh_from_db()

        self.assertEqual(self.seller1_credit.credit, 950000)  # 1,000,000 - 50,000
        self.assertEqual(self.seller2_credit.credit, 925000)  # 1,000,000 - 75,000
        self.assertEqual(self.phone1.credit, 125000)  # 50,000 + 75,000

    def test_transaction_logging(self):
        """Test transaction logging for recharges"""
        recharge_amount = 50000
        
        # Process recharge
        RechargeProcessRepository.selling_charge_to_phone_number(
            user=self.seller1,
            amount=recharge_amount,
            phone_number=self.phone1.number
        )

        # Verify transaction logs
        credit_transaction = TransactionLog.objects.filter(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE
        ).first()
        
        recharge_transaction = TransactionLog.objects.filter(
            seller=self.seller1,
            type=TransactionLog.RECHARGE,
            action_type=TransactionLog.INCREASE
        ).first()

        self.assertIsNotNone(credit_transaction)
        self.assertIsNotNone(recharge_transaction)
        self.assertEqual(credit_transaction.amount, recharge_amount)
        self.assertEqual(recharge_transaction.amount, recharge_amount)

    def test_invalid_phone_number(self):
        """Test recharge with invalid phone number"""
        with self.assertRaises(ValueError):
            RechargeProcessRepository.selling_charge_to_phone_number(
                user=self.seller1,
                amount=50000,
                phone_number='invalid_number'
            )

    def test_recharge_validation(self):
        # Negative amount
        with self.assertRaises(ValidationError):
            RechargeProcessRepository.selling_charge_to_phone_number(
                user=self.seller1,
                amount=-50000,
                phone_number=self.phone1.number
            )

        # Zero amount
        with self.assertRaises(ValidationError):
            RechargeProcessRepository.selling_charge_to_phone_number(
                user=self.seller1,
                amount=0,
                phone_number=self.phone1.number
            )
