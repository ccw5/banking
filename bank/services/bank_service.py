from datetime import datetime, timedelta
from decimal import Decimal, getcontext
from typing import Dict, List, Tuple

from bank.models.account import BankAccount
from bank.models.interest_rule import InterestRule
from bank.models.transaction import Deposit, Transaction, Withdrawal, Interest

getcontext().prec = 6

class BankService:
    def __init__(self):
        self.accounts: Dict[str, BankAccount] = {}
        self.interest_rules: List[InterestRule] = []

    def get_account_statement(self, account_id: str, year: int, month: int) -> List[Dict]:
        """Generates monthly statement with running balances and interest"""
        account = self._get_account(account_id)
        last_day = self._get_last_day_of_month(year, month)
        
        starting_balance = self._get_starting_balance(account, year, month)
        monthly_transactions = self._get_monthly_transactions(account, year, month)
        
        # Process all transactions except those on last day
        regular_transactions = [t for t in monthly_transactions if t.date != last_day]
        running_balance, statement_lines = self._process_transactions(
            regular_transactions, starting_balance)
        
        # Add interest if applicable
        if monthly_transactions:
            interest = self.calculate_interest_for_month(account_id, year, month)
            if interest > 0:
                running_balance += interest
                statement_lines.append({
                    'date': last_day,
                    'txn_id': '',
                    'type': 'I',
                    'amount': interest,
                    'balance': running_balance
                })
        
        return statement_lines

    def calculate_interest_for_month(self, account_id: str, year: int, month: int) -> Decimal:
        """Calculates monthly interest based on daily balances and interest rules"""
        account = self._get_account(account_id)
        first_day = datetime(year, month, 1)
        last_day = self._get_last_day_of_month(year, month)
        
        starting_balance = self._get_starting_balance(account, year, month)
        monthly_transactions = self._get_monthly_transactions(account, year, month)
        applicable_rules = sorted(
            [r for r in self.interest_rules if r.date <= last_day],
            key=lambda r: r.date
        )
        
        periods = self._calculate_interest_periods(first_day, last_day, applicable_rules)
        return self._calculate_interest(periods, monthly_transactions, starting_balance)

    def create_account_if_not_exists(self, account_id: str) -> BankAccount:
        """Creates account if it doesn't exist, otherwise returns existing"""
        if account_id not in self.accounts:
            self.accounts[account_id] = BankAccount(account_id)
        return self.accounts[account_id]
    
    def add_transaction(self, account_id: str, date: datetime, 
                       transaction_type: str, amount: Decimal) -> Transaction:
        """Adds a new transaction to the specified account"""
        account = self.create_account_if_not_exists(account_id)
        
        # Generate transaction ID
        date_str = date.strftime("%Y%m%d")
        same_day_transactions = [t for t in account.transactions 
                               if t.date.strftime("%Y%m%d") == date_str]
        transaction_id = f"{date_str}-{len(same_day_transactions)+1:02d}"
        
        if transaction_type.upper() == 'D':
            transaction = Deposit(account_id, date, amount, transaction_id)
        elif transaction_type.upper() == 'W':
            transaction = Withdrawal(account_id, date, amount, transaction_id)
        else:
            raise ValueError("Invalid transaction type")
        
        account.add_transaction(transaction)
        return transaction
    
    def add_interest_rule(self, date: datetime, rule_id: str, rate: Decimal):
        """Adds or updates an interest rate rule"""
        # Remove any existing rule for the same date
        self.interest_rules = [r for r in self.interest_rules if r.date != date]
        self.interest_rules.append(InterestRule(date, rule_id, rate))
        # Keep rules sorted by date
        self.interest_rules.sort(key=lambda r: r.date)

    # ========== HELPER METHODS ==========

    def _get_account(self, account_id: str) -> BankAccount:
        """Returns account or raises error if not found"""
        if account_id not in self.accounts:
            raise ValueError("Account not found")
        return self.accounts[account_id]

    def _get_monthly_transactions(self, account: BankAccount, 
                                year: int, month: int) -> List[Transaction]:
        """Returns sorted transactions for specified month"""
        return sorted(
            [t for t in account.transactions 
             if t.date.year == year and t.date.month == month],
            key=lambda t: t.date
        )

    def _get_starting_balance(self, account: BankAccount, 
                            year: int, month: int) -> Decimal:
        """Calculates balance at start of month (end of previous month)"""
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1
        return account.calculate_balance_up_to(
            self._get_last_day_of_month(prev_year, prev_month)
        )

    def _process_transactions(self, transactions: List[Transaction], 
                            start_balance: Decimal) -> Tuple[Decimal, List[Dict]]:
        """Processes transactions and returns final balance with statement lines"""
        running_balance = start_balance
        statement_lines = []
        
        for txn in transactions:
            running_balance = txn.apply(running_balance)
            statement_lines.append({
                'date': txn.date,
                'txn_id': txn.transaction_id,
                'type': 'D' if isinstance(txn, Deposit) else 'W',
                'amount': txn.amount,
                'balance': running_balance
            })
        
        return running_balance, statement_lines

    def _calculate_interest_periods(self, start_date: datetime, end_date: datetime, 
                                  rules: List[InterestRule]) -> List[Dict]:
        """Calculates interest periods between dates based on rules"""
        periods = []
        current_date = start_date
        
        # If no rules, use 0% for whole period
        if not rules:
            return [{
                'start': start_date,
                'end': end_date,
                'rate': Decimal('0')
            }]
        
        # Create periods between rule changes
        for i in range(len(rules)):
            rule = rules[i]
            period_start = max(rule.date, current_date)
            
            if i < len(rules) - 1:
                period_end = rules[i+1].date - timedelta(days=1)
            else:
                period_end = end_date
                
            if period_start <= period_end:
                periods.append({
                    'start': period_start,
                    'end': period_end,
                    'rate': Decimal(str(rule.rate / 100))
                })
                current_date = period_end + timedelta(days=1)
        
        # Add initial period if needed
        if not periods or periods[0]['start'] > start_date:
            initial_rate = Decimal(str(rules[0].rate / 100)) if rules else Decimal('0')
            periods.insert(0, {
                'start': start_date,
                'end': periods[0]['start'] - timedelta(days=1) if periods else end_date,
                'rate': initial_rate
            })
        
        return periods

    def _calculate_interest(self, periods: List[Dict], 
                          transactions: List[Transaction],
                          starting_balance: Decimal) -> Decimal:
        """Calculates interest for given periods and transactions"""
        total_interest = Decimal('0')
        current_balance = starting_balance
        transaction_index = 0
        
        for period in periods:
            period_start = period['start']
            period_end = period['end']
            rate = period['rate']
            
            # Process transactions during this period
            while (transaction_index < len(transactions) and
                   transactions[transaction_index].date <= period_end):
                txn = transactions[transaction_index]
                
                if txn.date < period_start:
                    transaction_index += 1
                    continue
                
                # Calculate interest before this transaction
                days_before = (txn.date - period_start).days
                if days_before > 0:
                    total_interest += current_balance * rate * Decimal(days_before) / Decimal('365')
                
                # Update balance with transaction
                current_balance = txn.apply(current_balance)
                period_start = txn.date
                transaction_index += 1
            
            # Calculate interest for remaining days
            days_remaining = (period_end - period_start).days + 1
            if days_remaining > 0:
                total_interest += current_balance * rate * Decimal(days_remaining) / Decimal('365')
        
        return total_interest.quantize(Decimal('0.00'))

    def _get_last_day_of_month(self, year: int, month: int) -> datetime:
        """Returns the last day of the specified month"""
        if month == 12:
            return datetime(year, 12, 31)
        return datetime(year, month + 1, 1) - timedelta(days=1)