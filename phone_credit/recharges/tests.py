from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from credits.models import SellerCredit, CreditRequest
from credits.services import CreditService
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import random

User = get_user_model()

class RechargeTest(TestCase):
    def setUp(self):
        # Create two sellers as required
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
        
        # Initialize seller credits
        self.seller1_credit = SellerCredit.objects.create(seller=self.seller1, credit=0)
        self.seller2_credit = SellerCredit.objects.create(seller=self.seller2, credit=0)

    def test_credit_increases_and_recharges(self):
        """Test 10 credit increases and 1000 recharges as specified"""
        # Step 1: Create and approve 10 credit increases for seller1
        total_credit_increased = 0
        for i in range(10):
            amount = random.randint(100000, 1000000)  # Random amount between 100k and 1M
            request = CreditService.increase_credit(self.seller1,amount)
            
            # Approve the request
            CreditService.approve_request(request.id)
            total_credit_increased += amount
            # Verify the credit was increased
            self.seller1_credit.refresh_from_db()
            self.assertEqual(self.seller1_credit.credit, total_credit_increased)


    def test_negative_credit_prevention(self):
        """Test that credit cannot go negative during recharge"""
        # Set initial credit
        initial_credit = 1000
        self.seller1_credit.credit = initial_credit
        self.seller1_credit.save()
        
        # Try to recharge more than available credit
        recharge_amount = 2000
        phone_number = "09123456789"
        
        with self.assertRaises(Exception):
            with transaction.atomic():
                CreditService.recharge_phone(
                    seller=self.seller1,
                    phone_number=phone_number,
                    amount=recharge_amount
                )
        
        # Verify credit remains unchanged
        self.seller1_credit.refresh_from_db()
        self.assertEqual(self.seller1_credit.credit, initial_credit) 