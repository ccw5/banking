import unittest
from datetime import datetime

from bank.utils.date_utils import parse_date, get_last_day_of_month

class TestDateUtils(unittest.TestCase):
    def test_parse_date_valid(self):
        date = parse_date("20230615")
        self.assertEqual(date, datetime(2023, 6, 15))

    def test_parse_date_invalid(self):
        with self.assertRaises(ValueError):
            parse_date("2023-06-15")
        
        with self.assertRaises(ValueError):
            parse_date("202306")

    def test_get_last_day_of_month(self):
        # June
        self.assertEqual(get_last_day_of_month(2023, 6), datetime(2023, 6, 30))
        # February non-leap
        self.assertEqual(get_last_day_of_month(2023, 2), datetime(2023, 2, 28))
        # February leap
        self.assertEqual(get_last_day_of_month(2024, 2), datetime(2024, 2, 29))
        # December
        self.assertEqual(get_last_day_of_month(2023, 12), datetime(2023, 12, 31))