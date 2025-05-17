from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import TransactionLog
from credits.models import SellerCredit
from recharges.models import PhoneNumber
from django.db import models

User = get_user_model()

class TransactionModelTests(TestCase):
    def setUp(self):
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
        
        self.seller1_credit = SellerCredit.objects.create(
            seller=self.seller1,
            credit=1000000  # 1,000,000 Toman
        )
        self.seller2_credit = SellerCredit.objects.create(
            seller=self.seller2,
            credit=1000000  # 1,000,000 Toman
        )
        
        self.phone = PhoneNumber.objects.create(
            number='+989123456789',
            credit=0
        )

    def test_transaction_creation(self):
        """Test basic transaction creation"""
        transaction = TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE,
            amount=50000,
            description="Test transaction"
        )
        
        self.assertEqual(transaction.seller, self.seller1)
        self.assertEqual(transaction.type, TransactionLog.CREDIT)
        self.assertEqual(transaction.action_type, TransactionLog.DECREASE)
        self.assertEqual(transaction.amount, 50000)

    def test_transaction_ordering(self):
        """Test transaction ordering by creation date"""
        transaction2 = TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE,
            amount=50000,
            description="Second transaction"
        )
        
        transaction1 = TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE,
            amount=30000,
            description="First transaction"
        )
        
        transactions = TransactionLog.objects.all()
        self.assertEqual(transactions[0], transaction1)
        self.assertEqual(transactions[1], transaction2)

    def test_transaction_types(self):
        """Test different transaction types"""
        credit_transaction = TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE,
            amount=50000,
            description="Credit decrease"
        )
        
        recharge_transaction = TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.RECHARGE,
            action_type=TransactionLog.INCREASE,
            amount=50000,
            description="Recharge increase"
        )
        
        self.assertEqual(credit_transaction.type, TransactionLog.CREDIT)
        self.assertEqual(recharge_transaction.type, TransactionLog.RECHARGE)

    def test_transaction_action_types(self):
        """Test different transaction action types"""
        increase_transaction = TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.INCREASE,
            amount=50000,
            description="Credit increase"
        )
        
        decrease_transaction = TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE,
            amount=30000,
            description="Credit decrease"
        )
        
        self.assertEqual(increase_transaction.action_type, TransactionLog.INCREASE)
        self.assertEqual(decrease_transaction.action_type, TransactionLog.DECREASE)

    def test_multiple_seller_transactions(self):
        """Test transactions from multiple sellers"""
        TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE,
            amount=50000,
            description="Seller 1 transaction"
        )
        
        TransactionLog.objects.create(
            seller=self.seller2,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE,
            amount=75000,
            description="Seller 2 transaction"
        )
        
        seller1_transactions = TransactionLog.objects.filter(seller=self.seller1)
        seller2_transactions = TransactionLog.objects.filter(seller=self.seller2)
        
        self.assertEqual(seller1_transactions.count(), 1)
        self.assertEqual(seller2_transactions.count(), 1)
        self.assertEqual(seller1_transactions.first().amount, 50000)
        self.assertEqual(seller2_transactions.first().amount, 75000)

    def test_transaction_description(self):
        """Test transaction description field"""
        description = "Test transaction description"
        transaction = TransactionLog.objects.create(
            seller=self.seller1,
            type=TransactionLog.CREDIT,
            action_type=TransactionLog.DECREASE,
            amount=50000,
            description=description
        )
        
        self.assertEqual(transaction.description, description)

    def test_transaction_consistency(self):
        """Test transaction consistency with credit operations"""
        transactions = [
            (TransactionLog.CREDIT, TransactionLog.INCREASE, 100000),
            (TransactionLog.CREDIT, TransactionLog.DECREASE, 50000),
            (TransactionLog.RECHARGE, TransactionLog.INCREASE, 25000),
            (TransactionLog.CREDIT, TransactionLog.DECREASE, 25000)
        ]
        
        for type_, action_type, amount in transactions:
            TransactionLog.objects.create(
                seller=self.seller1,
                type=type_,
                action_type=action_type,
                amount=amount,
                description=f"{type_} {action_type} for {amount}"
            )
        
        self.assertEqual(TransactionLog.objects.count(), len(transactions))
        
        total_amount = sum(amount for _, _, amount in transactions)
        self.assertEqual(
            TransactionLog.objects.aggregate(total=models.Sum('amount'))['total'],
            total_amount
        )
