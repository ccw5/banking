from datetime import datetime, timedelta

def parse_date(date_str: str) -> datetime:
    if len(date_str) != 8 or not date_str.isdigit():
        raise ValueError("Date should be in YYYYMMDD format")
    return datetime(int(date_str[:4]), int(date_str[4:6]), int(date_str[6:8]))

def get_last_day_of_month(year: int, month: int) -> datetime:
    if month == 12:
        return datetime(year, 12, 31)
    return datetime(year, month + 1, 1) - timedelta(days=1)