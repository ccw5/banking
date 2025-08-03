import unittest
from datetime import datetime
from decimal import Decimal

from bank.models.account import BankAccount
from bank.models.transaction import Deposit, Withdrawal

class TestBankAccount(unittest.TestCase):
    def setUp(self):
        self.account = BankAccount("AC001")
        self.test_date = datetime(2023, 6, 26)
        self.deposit = Deposit("AC001", self.test_date, Decimal('100.00'))
        self.withdrawal = Withdrawal("AC001", self.test_date, Decimal('50.00'))

    def test_initial_balance(self):
        self.assertEqual(self.account.balance, Decimal('0'))

    def test_add_deposit_transaction(self):
        self.account.add_transaction(self.deposit)
        self.assertEqual(self.account.balance, Decimal('100.00'))
        self.assertEqual(len(self.account.transactions), 1)

    def test_add_withdrawal_transaction(self):
        self.account.add_transaction(self.deposit)  # Need funds first
        self.account.add_transaction(self.withdrawal)
        self.assertEqual(self.account.balance, Decimal('50.00'))
        self.assertEqual(len(self.account.transactions), 2)

    def test_get_transactions_for_month(self):
        may_date = datetime(2023, 5, 15)
        may_deposit = Deposit("AC001", may_date, Decimal('200.00'))
        
        self.account.add_transaction(may_deposit)
        self.account.add_transaction(self.deposit)
        
        june_transactions = self.account.get_transactions_for_month(2023, 6)
        self.assertEqual(len(june_transactions), 1)
        self.assertEqual(june_transactions[0].amount, Decimal('100.00'))

    def test_calculate_balance_up_to_date(self):
        date1 = datetime(2023, 6, 1)
        date2 = datetime(2023, 6, 15)
        date3 = datetime(2023, 6, 30)
        
        deposit1 = Deposit("AC001", date1, Decimal('100.00'))
        deposit2 = Deposit("AC001", date2, Decimal('200.00'))
        
        self.account.add_transaction(deposit1)
        self.account.add_transaction(deposit2)
        
        balance = self.account.calculate_balance_up_to(date1)
        self.assertEqual(balance, Decimal('100.00'))
        
        balance = self.account.calculate_balance_up_to(date2)
        self.assertEqual(balance, Decimal('300.00'))