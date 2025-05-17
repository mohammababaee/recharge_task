from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor

from credits.models import SellerCredit, CreditRequest, TransactionLog
from credits.services import CreditService
from recharges.services import RechargePhoneNumberService
from recharges.models import PhoneNumber

User = get_user_model()


class RechargeTest(TransactionTestCase):
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
        self.seller1_credit = SellerCredit.objects.create(seller=self.seller1, credit=0)
        self.seller2_credit = SellerCredit.objects.create(seller=self.seller2, credit=0)

    def test_concurrent_recharges(self):
        for _ in range(10):
            req = CreditService.increase_credit(self.seller1,amount=500000)
            CreditService.approve_request(request_id=req.id)
        # print(User.objects.all())
        def recharge_worker(seller_id, start_idx, count):
            print(User.objects.all())
            print(SellerCredit.objects.all())
            seller = User.objects.get(id=seller_id)
            credit = SellerCredit.objects.get(seller=seller)
            for i in range(count):
                print(SellerCredit.objects.all())
                phone_number = f"0912345{start_idx + i:04d}"
                PhoneNumber.objects.create(number=phone_number,credit=0)
                RechargePhoneNumberService.charge_phone_number(seller, 5000, phone_number)

        # Simulate 1000 recharges using 10 threads
        num_threads = 10
        total_recharges = 1000
        per_thread = total_recharges // num_threads

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for i in range(num_threads):
                start = i * per_thread
                futures.append(
                    executor.submit(recharge_worker, self.seller1.id, start, per_thread)
                )
            for f in futures:
                f.result()


        self.seller1_credit.refresh_from_db()
        self.assertEqual(self.seller1_credit.credit, 5_000_000 - 1000 * 5000)

        self.assertEqual(
            TransactionLog.objects.filter(seller=self.seller1, type=TransactionLog.RECHARGE).count(),
            1000
        )

    def test_negative_credit_prevention(self):
        """Test that credit cannot go negative during recharge"""
        initial_credit = 1000
        self.seller1_credit.credit = initial_credit
        self.seller1_credit.save()

        recharge_amount = 2000
        phone_number = "09123456789"

        with self.assertRaises(Exception):
            CreditService.recharge_phone(
                seller=self.seller1,
                phone_number=phone_number,
                amount=recharge_amount
            )

        self.seller1_credit.refresh_from_db()
        self.assertEqual(self.seller1_credit.credit, initial_credit)
