# tests/test_history_basic.py
"""
python -m tests.test_history_basic

"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api.history import get_history_for_symbol


def test_history(symbol: str):
    print("=" * 40)
    print(f"Testing history for: {symbol}")

    try:
        hist = get_history_for_symbol(symbol, limit=10)
    except Exception as e:
        print(f"[NETWORK ERROR] نتوانستم تاريخچه را براي {symbol} بگيرم.")
        print(f"جزئيات خطا: {e}")
        print("=" * 40)
        return

    print(f"Records: {len(hist)}")
    for row in hist:
        print(row["date"], row["close"], row["volume"])
    print("=" * 40)


if __name__ == "__main__":
    for sym in ["فملی", "فولاد", "خساپا"]:
        test_history(sym)