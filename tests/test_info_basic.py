# tests/test_info_basic.py
from __future__ import annotations

"""
تست ساده برای اطلاعات نماد و فرمت پیام.

هدف:
- اگر اینترنت و TSETMC در دسترس باشند:
    * تلاش می‌کنیم برای چند نماد واقعی (مثلا فملی، فولاد، خساپا) اطلاعات را از api.main بگیریم
    * پیام فرمت‌شده را چاپ می‌کنیم.
- اگر اینترنت/SSL/Timeout مشکل داشته باشد:
    * خطا را می‌گیریم و پیام [NETWORK ERROR] چاپ می‌کنیم، اما کرش نمی‌کنیم.
- در هر صورت، در انتهای کار، یک تست آفلاین با داده‌ی ساختگی اجرا می‌کنیم
  تا مطمئن شویم format_stock_message درست کار می‌کند.
"""

from api.main import get_stock_info, format_stock_message


TEST_SYMBOLS = ["وآوا"]


def test_real_info():
    print("=== تست اطلاعات واقعی از TSETMC (آنلاین، ممکن است به خاطر شبکه خطا بدهد) ===")
    for sym in TEST_SYMBOLS:
        print("========================================")
        print(f"Testing symbol: {sym}")
        try:
            info = get_stock_info(sym)
        except Exception as e:
            print(f"[NETWORK ERROR] نتوانستم اطلاعات را براي {sym} بگيرم.")
            print(f"جزئيات خطا: {e}")
            continue

        if not info:
            print(f"[NO DATA] get_stock_info براي {sym} چيزي برنگرداند.")
            continue

        print("info =", info)
        print("----------------------------------------")
        formatted = format_stock_message(info)
        print("Formatted message:")
        print(formatted)
        print("========================================")

    print("=== پايان تست (اگر بالا خطا بود، طبيعي است) ===\n")

#offline test
def test_format_with_dummy():
    print("=== تست فرمت‌دهی با دادهٔ ساختگی (بدون نياز به اينترنت) ===")

    dummy_info = {
        "symbol": "فملی",
        "name": "ملي صنايع مس ايران",
        "sector": "فلزات اساسي",
        "last_price": 10000,
        "last_trade": 10100,
        "yesterday_price": 9800,
        "percent_change": 2.04,
        "percent_change_precise": 2.04,
        "volume": 12345678,
        "value": 987654321000,
        "trades": 4321,
        "market_cap": 250_000_000_000_000,
        "date": "1403/09/16",
        "time": "12:30:00",
        "last_update": "1403-09-16 12:31",
    }

    formatted = format_stock_message(dummy_info)
    print("Formatted dummy message:")
    print(formatted)
    print("=== پايان تست فرمت ساختگی ===")


if __name__ == "__main__":
    test_real_info()
    test_format_with_dummy()
