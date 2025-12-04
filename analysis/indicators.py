# analysis/indicators.py
from __future__ import annotations

from typing import List, Optional, Sequence


def compute_sma(values: Sequence[float], window: int) -> Optional[float]:
    """
    Simple Moving Average (SMA)

    - ورودی: لیست قیمت‌ها (values) و طول پنجره (window)
    - خروجی: میانگین n تا قیمت آخر.
      مثال: اگر window=20 باشد، میانگین ۲۰ روز اخیر را می‌دهد.

    اگر تعداد داده‌ها کمتر از window باشد → None برمی‌گرداند.
    """

    if window <= 0:
        return None

    if len(values) < window:
        # No enough data
        return None

    # last but not least
    window_slice = values[-window:]
    return sum(window_slice) / float(window)


def compute_rsi(values: Sequence[float], period: int = 14) -> Optional[float]:
    """
    Relative Strength Index (RSI) – نسخه ساده

    - تغییر روزانه = قیمت امروز - قیمت دیروز
    - اگر تغییر مثبت بود → gain
    - اگر تغییر منفی بود → loss (قدر مطلق منفی‌ها)

      avg_gain = میانگین gain های 14 روز اخیر
      avg_loss = میانگین loss های 14 روز اخیر

      RS = avg_gain / avg_loss
      RSI = 100 - (100 / (1 + RS))

    اگر داده کافی نباشد → None برمی‌گرداند.
    """

    if period <= 0:
        return None

    if len(values) <= period:
        # برای RSI حداقل period+1 قیمت لازم داریم
        return None

    gains: List[float] = []
    losses: List[float] = []

    # تغییرات روزانه را حساب می‌کنیم
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(-change)

    # فقط period تغییر آخر را برای محاسبه میانگین استفاده می‌کنیم
    gains = gains[-period:]
    losses = losses[-period:]

    if len(gains) == 0 or len(losses) == 0:
        return None

    avg_gain = sum(gains) / float(period)
    avg_loss = sum(losses) / float(period)

    if avg_loss == 0:
        # یعنی همه (یا تقریبا همه) روزها مثبت بوده → RSI نزدیک 100
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def percent_change(current: float, previous: float) -> Optional[float]:
    """
    درصد تغییر بین دو عدد.
    ex)
      previous = 100
      current = 110
      => (110 - 100) / 100 * 100 = 10%

    اگر previous صفر باشد (تقسیم بر صفر) → None
    """

    try:
        if previous == 0:
            return None
        return (current - previous) / float(previous) * 100.0
    except Exception:
        return None


if __name__ == "__main__":
    prices = [10, 11, 12, 13, 14, 15, 16]
    print("SMA(3) =", compute_sma(prices, 3))
    print("RSI(14) روی همین داده کوتاه =", compute_rsi(prices, 14))
