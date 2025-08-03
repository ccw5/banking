from datetime import datetime
from decimal import Decimal

class InterestRule:
    def __init__(self, date: datetime, rule_id: str, rate: Decimal):
        self.date = date
        self.rule_id = rule_id
        self.rate = rate