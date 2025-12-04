# tests/test_info_basic.py
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api.main import get_stock_info, format_stock_message


def test_single_symbol(symbol: str):
    print("=" * 40)
    print(f"Testing symbol: {symbol}")
    info = get_stock_info(symbol)
    print("info =", info)
    print("-" * 40)
    print("Formatted message:")
    print(format_stock_message(info))
    print("=" * 40)


if __name__ == "__main__":
    for sym in ["فملی", "وآوا", "خساپا"]:
        test_single_symbol(sym)
