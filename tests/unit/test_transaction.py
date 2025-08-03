# tests/unit/test_transaction.py
import unittest
from datetime import datetime
from decimal import Decimal

from bank.models.transaction import Deposit, Withdrawal, Interest

class TestTransactionModels(unittest.TestCase):
    def setUp(self):
        self.test_date = datetime(2023, 6, 26)
        self.account_id = "AC001"
        self.amount = Decimal('100.00')

    def test_deposit_application(self):
        deposit = Deposit(self.account_id, self.test_date, self.amount)
        new_balance = deposit.apply(Decimal('50.00'))
        self.assertEqual(new_balance, Decimal('150.00'))

    def test_withdrawal_application_sufficient_funds(self):
        withdrawal = Withdrawal(self.account_id, self.test_date, self.amount)
        new_balance = withdrawal.apply(Decimal('150.00'))
        self.assertEqual(new_balance, Decimal('50.00'))

    def test_withdrawal_application_insufficient_funds(self):
        withdrawal = Withdrawal(self.account_id, self.test_date, self.amount)
        with self.assertRaises(ValueError):
            withdrawal.apply(Decimal('50.00'))

    def test_interest_application(self):
        interest = Interest(self.account_id, self.test_date, self.amount)
        new_balance = interest.apply(Decimal('50.00'))
        self.assertEqual(new_balance, Decimal('150.00'))