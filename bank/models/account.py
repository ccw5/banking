# bank/models/account.py
from __future__ import annotations
from datetime import datetime
from decimal import Decimal
from typing import List

from bank.models.transaction import Transaction

class BankAccount:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.transactions: List[Transaction] = []
        self.balance = Decimal('0')
    
    def add_transaction(self, transaction: 'Transaction'):
        self.balance = transaction.apply(self.balance)
        self.transactions.append(transaction)
    
    def get_transactions_for_month(self, year: int, month: int) -> List[Transaction]:
        return [t for t in self.transactions 
                if t.date.year == year and t.date.month == month]
    
    def calculate_balance_up_to(self, date: datetime) -> Decimal:
        balance = Decimal('0')
        for transaction in sorted(self.transactions, key=lambda t: t.date):
            if transaction.date <= date:
                balance = transaction.apply(balance)
        return balance