# tests/test_indicators.py
from __future__ import annotations
import sys
import os
import math
from analysis.indicators import compute_sma, compute_rsi, percent_change

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
def test_sma_basic():
    prices = [10, 11, 12, 13, 14]
    sma_3 = compute_sma(prices, 3)
    sma_5 = compute_sma(prices, 5)
    sma_10 = compute_sma(prices, 10)

    print("prices:", prices)
    print("SMA(3):", sma_3)
    print("SMA(5):", sma_5)
    print("SMA(10):", sma_10)

    # یک چک ساده برای مطمئن شدن
    assert round(sma_3, 2) == round((12 + 13 + 14) / 3, 2)
    assert round(sma_5, 2) == round(sum(prices) / 5, 2)
    assert sma_10 is None  # چون داده کمتر از 10 است


def test_rsi_basic():
    # یک سری قیمت که هم صعودی دارد هم نزولی
    prices = [10, 11, 9, 10, 12, 11, 13, 15, 14, 16, 17, 16, 18, 20, 19]

    rsi_14 = compute_rsi(prices, period=14)
    print("prices:", prices)
    print("RSI(14):", rsi_14)

    # فقط چک می‌کنیم که:
    # - None نباشد
    # - بین 0 و 100 باشد
    assert rsi_14 is not None
    assert 0 <= rsi_14 <= 100


def test_percent_change():
    print("percent_change(110, 100):", percent_change(110, 100))
    print("percent_change(90, 100):", percent_change(90, 100))
    print("percent_change(100, 0):", percent_change(100, 0))

    assert round(percent_change(110, 100), 2) == 10.00
    assert round(percent_change(90, 100), 2) == -10.00
    assert percent_change(100, 0) is None  # تقسیم بر صفر


if __name__ == "__main__":
    print("=== Testing SMA ===")
    test_sma_basic()
    print("=== Testing RSI ===")
    test_rsi_basic()
    print("=== Testing percent_change ===")
    test_percent_change()
    print("All indicator tests passed (if no AssertionError was raised).")
