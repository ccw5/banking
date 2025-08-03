from datetime import datetime
from decimal import Decimal
from bank.models.transaction import Interest
from bank.services.bank_service import BankService
from bank.utils.date_utils import parse_date

class BankConsoleUI:
    def __init__(self, bank_service: BankService):
        self.bank_service = bank_service
    
    def run(self):
        print("Welcome to AwesomeGIC Bank! What would you like to do?")
        while True:
            print("[T] Input transactions")
            print("[I] Define interest rules")
            print("[P] Print statement")
            print("[Q] Quit")
            choice = input("> ").strip().upper()
            
            if choice == 'T':
                self.handle_transaction_input()
            elif choice == 'I':
                self.handle_interest_rule_input()
            elif choice == 'P':
                self.handle_statement_print()
            elif choice == 'Q':
                print("\nThank you for banking with AwesomeGIC Bank.")
                print("Have a nice day!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def handle_transaction_input(self):
        print("\nPlease enter transaction details in <Date> <Account> <Type> <Amount> format")
        print("(or enter blank to go back to main menu):")
        while True:
            input_str = input("> ").strip()
            if not input_str:
                break
            
            try:
                parts = input_str.split()
                if len(parts) != 4:
                    raise ValueError("Invalid input format")
                
                date_str, account_id, txn_type, amount_str = parts
                date = self._parse_date(date_str)
                amount = Decimal(amount_str)
                
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                
                transaction = self.bank_service.add_transaction(account_id, date, txn_type, amount)
                self._print_account_transactions(account_id)
                break
            except ValueError as e:
                print(f"Error: {str(e)}. Please try again.")
    
    def handle_interest_rule_input(self):
        print("\nPlease enter interest rules details in <Date> <RuleId> <Rate in %> format")
        print("(or enter blank to go back to main menu):")
        while True:
            input_str = input("> ").strip()
            if not input_str:
                break
            
            try:
                parts = input_str.split()
                if len(parts) != 3:
                    raise ValueError("Invalid input format")
                
                date_str, rule_id, rate_str = parts
                date = self._parse_date(date_str)
                rate = Decimal(rate_str)
                
                if not (0 < rate < 100):
                    raise ValueError("Rate must be between 0 and 100")
                
                self.bank_service.add_interest_rule(date, rule_id, rate)
                self._print_interest_rules()
                break
            except ValueError as e:
                print(f"Error: {str(e)}. Please try again.")
    
    def handle_statement_print(self):
        print("\nPlease enter account and month to generate the statement <Account> <Year><Month>")
        print("(or enter blank to go back to main menu):")
        while True:
            input_str = input("> ").strip()
            if not input_str:
                break
            
            try:
                parts = input_str.split()
                if len(parts) != 2:
                    raise ValueError("Invalid input format")
                
                account_id, month_str = parts
                if len(month_str) != 6 or not month_str.isdigit():
                    raise ValueError("Month should be in YYYYMM format")
                
                year = int(month_str[:4])
                month = int(month_str[4:6])
                
                if account_id not in self.bank_service.accounts:
                    raise ValueError("Account not found")
                
                interest = self.bank_service.calculate_interest_for_month(account_id, year, month)
                last_day = datetime(year, month, 
                                   self.bank_service._get_last_day_of_month(year, month).day)
                interest_transaction = Interest(account_id, last_day, interest)
                self.bank_service.accounts[account_id].add_transaction(interest_transaction)
                
                self._print_monthly_statement(account_id, year, month)
                break
            except ValueError as e:
                print(f"Error: {str(e)}. Please try again.")
    
    def _print_account_transactions(self, account_id: str):
        account = self.bank_service.accounts[account_id]
        print(f"\nAccount: {account_id}")
        print("| Date     | Txn Id      | Type | Amount |")
        for txn in sorted(account.transactions, key=lambda t: t.date):
            if isinstance(txn, Interest):
                continue  # Skip interest transactions in this view
            print(f"| {txn.date.strftime('%Y%m%d')} | {txn.transaction_id} | {txn.__class__.__name__[0]}    | {txn.amount:7.2f} |")
        print()
    
    def _print_interest_rules(self):
        print("\nInterest rules:")
        print("| Date     | RuleId | Rate (%) |")
        for rule in self.bank_service.interest_rules:
            print(f"| {rule.date.strftime('%Y%m%d')} | {rule.rule_id:6} | {rule.rate:8.2f} |")
        print()
    
    def _print_monthly_statement(self, account_id: str, year: int, month: int):
        statement_lines = self.bank_service.get_account_statement(account_id, year, month)
        
        print(f"\nAccount: {account_id}")
        print("| Date     | Txn Id      | Type | Amount | Balance |")
        
        for line in statement_lines:
            print(
                f"| {line['date'].strftime('%Y%m%d')} | "
                f"{line['txn_id']:11} | "
                f"{line['type']:4} | "
                f"{line['amount']:6.2f} | "
                f"{line['balance']:7.2f} |"
            )
            
    def _parse_date(self, date_str: str) -> datetime:
        if len(date_str) != 8 or not date_str.isdigit():
            raise ValueError("Date should be in YYYYMMDD format")
        year = int(date_str[:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        return datetime(year, month, day)

# Main entry point
if __name__ == "__main__":
    bank_service = BankService()
    ui = BankConsoleUI(bank_service)
    ui.run()