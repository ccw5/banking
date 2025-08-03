import unittest
from datetime import datetime
from decimal import Decimal

from bank.services.bank_service import BankService

class TestBankService(unittest.TestCase):
    def setUp(self):
        self.service = BankService()
        self.account_id = "AC001"
        self.test_date = datetime(2023, 6, 26)
        self.rule_id = "RULE01"
        self.rate = Decimal('1.95')

    def test_create_account_with_first_transaction(self):
        transaction = self.service.add_transaction(
            self.account_id, self.test_date, "D", Decimal('100.00')
        )
        self.assertIn(self.account_id, self.service.accounts)
        self.assertEqual(self.service.accounts[self.account_id].balance, Decimal('100.00'))
        self.assertEqual(transaction.transaction_id, "20230626-01")

    def test_transaction_id_generation(self):
        # First transaction
        txn1 = self.service.add_transaction(
            self.account_id, self.test_date, "D", Decimal('100.00')
        )
        self.assertEqual(txn1.transaction_id, "20230626-01")
        
        # Second transaction same day
        txn2 = self.service.add_transaction(
            self.account_id, self.test_date, "D", Decimal('50.00')
        )
        self.assertEqual(txn2.transaction_id, "20230626-02")
        
        # Different day
        new_date = datetime(2023, 6, 27)
        txn3 = self.service.add_transaction(
            self.account_id, new_date, "D", Decimal('25.00')
        )
        self.assertEqual(txn3.transaction_id, "20230627-01")

    def test_add_interest_rule(self):
        self.service.add_interest_rule(self.test_date, self.rule_id, self.rate)
        self.assertEqual(len(self.service.interest_rules), 1)
        self.assertEqual(self.service.interest_rules[0].rule_id, self.rule_id)

    def test_interest_calculation(self):
        # Setup transactions
        self.service.add_transaction(self.account_id, datetime(2023, 5, 5), "D", Decimal('100.00'))
        self.service.add_transaction(self.account_id, datetime(2023, 6, 1), "D", Decimal('150.00'))
        self.service.add_transaction(self.account_id, datetime(2023, 6, 26), "W", Decimal('20.00'))
        self.service.add_transaction(self.account_id, datetime(2023, 6, 26), "W", Decimal('100.00'))
        
        # Setup interest rules
        self.service.add_interest_rule(datetime(2023, 1, 1), "RULE01", Decimal('1.95'))
        self.service.add_interest_rule(datetime(2023, 5, 20), "RULE02", Decimal('1.90'))
        self.service.add_interest_rule(datetime(2023, 6, 15), "RULE03", Decimal('2.20'))
        
        interest = self.service.calculate_interest_for_month(self.account_id, 2023, 6)
        self.assertEqual(interest, Decimal('0.39'))

