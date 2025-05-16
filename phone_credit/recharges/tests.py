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
        """Test 10 credit increases and 50 recharges"""
        # Step 1: Create and approve 10 credit increases
        for i in range(10):
            request = CreditRequest.objects.create(
                seller=self.seller1,
                amount=1000000,  # 1M for each increase
                status=CreditRequest.PENDING
            )
            CreditService.approve_request(request.id)
        
        # Verify total credit
        self.seller1_credit.refresh_from_db()
        self.assertEqual(self.seller1_credit.credit, 10000000)  # 10M total

        # Step 2: Perform 50 recharge transactions
        def recharge_worker(seller_id, start_idx, count):
            from django.db import connection
            connection.close()
            
            seller = User.objects.get(id=seller_id)
            for i in range(count):
                phone_number = f"0912345{start_idx + i:04d}"
                with transaction.atomic():
                    CreditService.recharge_phone(
                        seller=seller,
                        phone_number=phone_number,
                        amount=5000
                    )

        # Run parallel recharge operations
        num_processes = min(multiprocessing.cpu_count(), 4)  # Limit to 4 processes
        iterations_per_process = 50 // num_processes
        
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = []
            for i in range(num_processes):
                start_idx = i * iterations_per_process
                futures.append(
                    executor.submit(
                        recharge_worker,
                        self.seller1.id,
                        start_idx,
                        iterations_per_process
                    )
                )
            
            # Wait for all processes to complete
            for future in futures:
                future.result()

        # Step 3: Verify final state
        self.seller1_credit.refresh_from_db()
        expected_credit = 10000000 - (50 * 5000)  # 10M - (50 * 5000)
        self.assertEqual(self.seller1_credit.credit, expected_credit)
        
        # Verify transaction records
        from transactions.models import TransactionLog
        self.assertEqual(
            TransactionLog.objects.filter(
                seller=self.seller1,
                transaction_type='recharge'
            ).count(),
            50
        )
        self.assertEqual(
            TransactionLog.objects.filter(
                seller=self.seller1,
                transaction_type='credit_increase'
            ).count(),
            10
        )



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