# bank/models/transaction.py
from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

class Transaction(ABC):
    def __init__(self, account_id: str, date: datetime, amount: Decimal, transaction_id: str = ""):
        self.account_id = account_id
        self.date = date
        self.amount = amount
        self.transaction_id = transaction_id
    
    @abstractmethod
    def apply(self, balance: Decimal) -> Decimal:
        pass

class Deposit(Transaction):
    def apply(self, balance: Decimal) -> Decimal:
        return balance + self.amount

class Withdrawal(Transaction):
    def apply(self, balance: Decimal) -> Decimal:
        if balance < self.amount:
            raise ValueError("Insufficient funds")
        return balance - self.amount

class Interest(Transaction):
    def apply(self, balance: Decimal) -> Decimal:
        return balance + self.amount