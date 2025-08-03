import unittest
from unittest.mock import patch
from io import StringIO
from datetime import datetime
from decimal import Decimal

from bank.ui.console_ui import BankConsoleUI
from bank.services.bank_service import BankService
from bank.models.transaction import Deposit, Withdrawal

class TestConsoleUI(unittest.TestCase):
    def setUp(self):
        self.service = BankService()
        self.ui = BankConsoleUI(self.service)
        
        # Setup test data
        self.service.add_transaction("AC001", datetime(2023, 5, 5), "D", Decimal('100.00'))
        self.service.add_transaction("AC001", datetime(2023, 6, 1), "D", Decimal('150.00'))
        self.service.add_transaction("AC001", datetime(2023, 6, 26), "W", Decimal('20.00'))
        self.service.add_transaction("AC001", datetime(2023, 6, 26), "W", Decimal('100.00'))
        
        # Only add June interest rules to prevent May interest
        self.service.add_interest_rule(datetime(2023, 6, 1), "RULE02", Decimal('1.90'))
        self.service.add_interest_rule(datetime(2023, 6, 15), "RULE03", Decimal('2.20'))

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['P', 'AC001 202306', '', 'Q'])
    def test_print_statement_with_interest(self, mock_input, mock_stdout):
        self.ui.run()
        output = mock_stdout.getvalue()
        
        # Check header
        self.assertIn("Account: AC001", output)
        self.assertIn("| Date     | Txn Id      | Type | Amount | Balance |", output)
        
        # Check transactions
        self.assertIn("| 20230601 | 20230601-01 | D    | 150.00 |  250.00 |", output)
        self.assertIn("| 20230626 | 20230626-01 | W    |  20.00 |  230.00 |", output)
        self.assertIn("| 20230626 | 20230626-02 | W    | 100.00 |  130.00 |", output)
        
        # Check interest appears exactly once
        self.assertEqual(output.count("20230630"), 1)
        self.assertIn("| 20230630 |             | I    |   0.39 |  130.39 |", output)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['P', 'AC001 202305', '', 'Q'])
    def test_print_statement_previous_month(self, mock_input, mock_stdout):
        self.ui.run()
        output = mock_stdout.getvalue()
        
        # May should only show the deposit with no interest
        self.assertIn("| 20230505 | 20230505-01 | D    | 100.00 |  100.00 |", output)
        self.assertNotIn("202306", output)  # No June transactions
        self.assertNotIn("I    |", output)  # No interest for May

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['P', 'AC001 202313', '', 'Q'])
    def test_print_statement_invalid_month(self, mock_input, mock_stdout):
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("Error: month must be in 1..12", output)  # Match actual error message

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['P', 'INVALID 202306', '', 'Q'])
    def test_print_statement_invalid_account(self, mock_input, mock_stdout):
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("Account not found", output)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['T', '20230626 AC001 W 20.00', '', 'P', 'AC001 202306', '', 'Q'])
    def test_transaction_flow(self, mock_input, mock_stdout):
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("20230626-03 | W    |  20.00 |", output)
        self.assertIn("| 20230626 | 20230626-03 | W    |  20.00 |  110.00 |", output)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('builtins.input', side_effect=['I', '20230615 RULE03 2.20', '', 'Q'])
    def test_interest_rule_flow(self, mock_input, mock_stdout):
        self.ui.run()
        output = mock_stdout.getvalue()
        self.assertIn("RULE03 |     2.20 |", output)

