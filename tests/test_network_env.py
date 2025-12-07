from __future__ import annotations

"""
تست ساده برای بررسی تنظیمات شبکه و پروکسی از روی فایل .env

اجرا:
    python -m tests.test_network_env
"""

import os
import textwrap
from typing import Optional

import requests
from dotenv import load_dotenv


for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
    if var in os.environ:
        print(f"[DEBUG] Removing {var} from process env for this test")
        os.environ.pop(var, None)


#.env
def load_env() -> None:
    """Load environment variables from .env file in project root."""
    env_loaded = load_dotenv()
    print(f"[INFO] .env loaded: {env_loaded}")
    print()


# helpers
def _get_bool_env(name: str, default: bool = False) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip() in ("1", "true", "True", "YES", "yes")


def _short_token(token: Optional[str]) -> str:
    """برای چاپ امن توکن (فقط چند کاراکتر اول/آخر)."""
    if not token:
        return "<EMPTY>"
    if len(token) <= 10:
        return token
    return f"{token[:6]}...{token[-4:]}"


#  تست ۱: نمایش تنظیمات 
def print_current_settings() -> None:
    print("=== CURRENT ENV / SETTINGS ===")
    print(f"HTTP_PROXY (OS)  = {os.environ.get('HTTP_PROXY')}")
    print(f"HTTPS_PROXY (OS) = {os.environ.get('HTTPS_PROXY')}")
    print()

    bot_token = os.getenv("BOT_TOKEN")
    print(f"BOT_TOKEN (masked)        = {_short_token(bot_token)}")

    telegram_proxy_enabled = _get_bool_env("TELEGRAM_PROXY_ENABLED", False)
    proxy_telegram = os.getenv("PROXY_TELEGRAM")

    use_proxy_tsetmc = _get_bool_env("USE_PROXY_TSETMC", False)
    proxy_tsetmc = os.getenv("PROXY_TSETMC")

    http_timeout = os.getenv("HTTP_TIMEOUT", "60")

    print(f"TELEGRAM_PROXY_ENABLED    = {telegram_proxy_enabled}")
    print(f"PROXY_TELEGRAM            = {proxy_telegram}")
    print(f"USE_PROXY_TSETMC          = {use_proxy_tsetmc}")
    print(f"PROXY_TSETMC              = {proxy_tsetmc}")
    print(f"HTTP_TIMEOUT              = {http_timeout}")
    print("=" * 40)
    print()


# تست ۲: اتصال به TSETMC
def test_tsetmc_connection() -> None:
    print("=== TEST: TSETMC connection ===")

    url = "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketMap?market=0&size=2&sector=0&typeSelected=1"

    use_proxy = _get_bool_env("USE_PROXY_TSETMC", False)
    proxy_url = os.getenv("PROXY_TSETMC")
    timeout = float(os.getenv("HTTP_TIMEOUT", "60"))

    if use_proxy and proxy_url:
        proxies = {
            "http": proxy_url,
            "https": proxy_url,
        }
        print(f"[INFO] Using proxy for TSETMC: {proxy_url}")
    else:
        proxies = None
        print("[INFO] Not using proxy for TSETMC (direct connection).")

    try:
        resp = requests.get(url, proxies=proxies, timeout=timeout)
        print(f"[OK] HTTP status: {resp.status_code}")
        text_sample = resp.text[:200].replace("\n", " ")
        print(f"[OK] Response sample: {text_sample!r}")
    except Exception as e:
        print("[ERROR] Could not connect to TSETMC.")
        print(f"Details: {e}")
    print("=" * 40)
    print()


# تست ۳: اتصال به Telegram API 
def test_telegram_connection() -> None:
    print("=== TEST: Telegram API connection ===")

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        print("[WARN] BOT_TOKEN is empty. Cannot test Telegram API.")
        print("=" * 40)
        print()
        return

    telegram_proxy_enabled = _get_bool_env("TELEGRAM_PROXY_ENABLED", False)
    proxy_telegram = os.getenv("PROXY_TELEGRAM")
    timeout = float(os.getenv("HTTP_TIMEOUT", "60"))

    if telegram_proxy_enabled and proxy_telegram:
        proxies = {
            "http": proxy_telegram,
            "https": proxy_telegram,
        }
        print(f"[INFO] Using proxy for Telegram: {proxy_telegram}")
    else:
        proxies = None
        print("[INFO] Not using proxy for Telegram (direct connection).")

    url = f"https://api.telegram.org/bot{bot_token}/getMe"

    try:
        resp = requests.get(url, proxies=proxies, timeout=timeout)
        print(f"[OK] HTTP status: {resp.status_code}")
        print(f"[OK] Response: {resp.text}")
    except Exception as e:
        print("[ERROR] Could not connect to Telegram API.")
        print(f"Details: {e}")
    print("=" * 40)
    print()


# main 
def main() -> None:
    print(
        textwrap.dedent(
            """
            ================================
            Network / Proxy diagnostics test
            ================================

            این اسکریپت:
              1) .env را لود می‌کند
              2) تنظیمات پروکسی و توکن را (به صورت امن) چاپ می‌کند
              3) اتصال به TSETMC را تست می‌کند
              4) اتصال به Telegram API را تست می‌کند

            اگر جایی خطا دیدی، متن خطا را برای عیب‌یابی نگه دار.
            """
        )
    )

    load_env()
    print_current_settings()
    test_tsetmc_connection()
    test_telegram_connection()


if __name__ == "__main__":
    main()
