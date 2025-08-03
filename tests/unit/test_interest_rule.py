import unittest
from datetime import datetime
from decimal import Decimal

from bank.models.interest_rule import InterestRule

class TestInterestRule(unittest.TestCase):
    def setUp(self):
        self.test_date = datetime(2023, 6, 1)
        self.rule_id = "RULE01"
        self.rate = Decimal('1.95')

    def test_interest_rule_creation(self):
        rule = InterestRule(self.test_date, self.rule_id, self.rate)
        self.assertEqual(rule.date, self.test_date)
        self.assertEqual(rule.rule_id, self.rule_id)
        self.assertEqual(rule.rate, self.rate)