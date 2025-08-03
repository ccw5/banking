from bank.services.bank_service import BankService
from bank.ui.console_ui import BankConsoleUI

def main():
    bank_service = BankService()
    ui = BankConsoleUI(bank_service)
    ui.run()

if __name__ == "__main__":
    main()