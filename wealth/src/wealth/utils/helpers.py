"""Helper utility functions."""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from zoneinfo import ZoneInfo


def format_price(price: float, decimals: int = 2) -> str:
    return f"{price:,.{decimals}f}"


def format_percent(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}%"


def format_volume(volume: float) -> str:
    if volume >= 1_000_000_000:
        return f"{volume / 1_000_000_000:.2f}B"
    elif volume >= 1_000_000:
        return f"{volume / 1_000_000:.2f}M"
    elif volume >= 1_000:
        return f"{volume / 1_000:.2f}K"
    return f"{volume:.0f}"


def format_currency(amount: float, currency: str = "CNY") -> str:
    symbols = {"CNY": "¥", "USD": "$", "HKD": "HK$", "EUR": "€", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}" if symbol else f"{amount:,.2f}"


def validate_date_range(
    start_date: Optional[str],
    end_date: Optional[str],
    max_days: int = 3650,
) -> Tuple[str, str]:
    if not end_date:
        end_date = datetime.now().strftime("%Y%m%d")
    if not start_date:
        end_dt = datetime.strptime(end_date, "%Y%m%d")
        start_dt = end_dt - timedelta(days=max_days)
        start_date = start_dt.strftime("%Y%m%d")

    start_dt = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")

    if start_dt > end_dt:
        start_date, end_date = end_date, start_date

    days_diff = (end_dt - start_dt).days
    if days_diff > max_days:
        end_dt = start_dt + timedelta(days=max_days)
        end_date = end_dt.strftime("%Y%m%d")

    return start_date, end_date


def parse_date(date_str: str, fmt: str = "%Y%m%d") -> Optional[datetime]:
    formats = ["%Y%m%d", "%Y-%m-%d", "%Y/%m/%d", "%Y%m%d %H:%M:%S"]
    for f in formats:
        try:
            return datetime.strptime(date_str, f)
        except ValueError:
            continue
    return None


def get_china_tz():
    return ZoneInfo("Asia/Shanghai")


def now_china():
    return datetime.now(get_china_tz())


def is_trading_day(date: Optional[datetime] = None) -> bool:
    if date is None:
        date = now_china()
    return date.weekday() < 5


def get_trading_days(start_date: datetime, end_date: datetime) -> list[datetime]:
    days = []
    current = start_date
    while current <= end_date:
        if is_trading_day(current):
            days.append(current)
        current += timedelta(days=1)
    return days
