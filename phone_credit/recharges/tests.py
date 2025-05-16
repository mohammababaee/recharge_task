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
            request = CreditRequest.objects.create(
                seller=self.seller1,
                amount=amount,
                status=CreditRequest.PENDING
            )
            
            # Approve the request
            CreditService.approve_request(request.id)
            total_credit_increased += amount
            
            # Verify the credit was increased
            self.seller1_credit.refresh_from_db()
            self.assertEqual(self.seller1_credit.credit, total_credit_increased)

        # Step 2: Perform 1000 recharge transactions
        recharge_amount = 5000
        phone_numbers = [f"0912345{i:04d}" for i in range(1000)]
        
        # Use multiprocessing for parallel execution
        num_processes = multiprocessing.cpu_count()
        iterations_per_process = 1000 // num_processes
        
        def recharge_worker(seller_id, phone_numbers, amount, start_idx, count):
            from django.db import connection
            connection.close()  # Close connection before forking
            
            seller = User.objects.get(id=seller_id)
            for i in range(count):
                phone_number = phone_numbers[start_idx + i]
                try:
                    with transaction.atomic():
                        CreditService.recharge_phone(
                            seller=seller,
                            phone_number=phone_number,
                            amount=amount
                        )
                except Exception as e:
                    print(f"Error in worker: {str(e)}")

        # Run parallel recharge operations
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = []
            for i in range(num_processes):
                start_idx = i * iterations_per_process
                futures.append(
                    executor.submit(
                        recharge_worker,
                        self.seller1.id,
                        phone_numbers,
                        recharge_amount,
                        start_idx,
                        iterations_per_process
                    )
                )
            
            # Wait for all processes to complete
            for future in futures:
                future.result()

        # Step 3: Validate final balances
        self.seller1_credit.refresh_from_db()
        expected_credit = total_credit_increased - (1000 * recharge_amount)
        self.assertEqual(self.seller1_credit.credit, expected_credit)
        
        # Verify transaction records
        from transactions.models import TransactionLog
        recharge_count = TransactionLog.objects.filter(
            seller=self.seller1,
            transaction_type='recharge'
        ).count()
        self.assertEqual(recharge_count, 1000)
        
        credit_increase_count = TransactionLog.objects.filter(
            seller=self.seller1,
            transaction_type='credit_increase'
        ).count()
        self.assertEqual(credit_increase_count, 10)

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