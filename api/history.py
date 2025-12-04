# api/history.py
from __future__ import annotations
from typing import List, Dict

from .main import fetch_market_map, normalize_symbol, session

DAILY_URL_TEMPLATE = (
    "http://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{ins_code}/0"
)


def get_inscode_for_symbol(symbol: str) -> str | None:
    """
    پیدا کردن insCode از روی نماد یا نام نماد.
    از همون مارکت‌مپ استفاده می‌کنیم.
    """
    sym = normalize_symbol(symbol)
    if not sym:
        return None

    items = fetch_market_map()

    for it in items:
        code = normalize_symbol(it.get("lVal18AFC", ""))
        name = normalize_symbol(it.get("lVal30", ""))
        if code == sym or name == sym:
            return it.get("insCode")

    return None


def _extract_daily_items(raw) -> List[Dict]:
    """
    چون ساختار JSON ممکنه کمی فرق کند، سعی می‌کنیم لیست رکوردها را پیدا کنیم.
    """
    if isinstance(raw, list):
        return raw

    if isinstance(raw, dict):
        for key in ["closingPriceDaily", "closingPriceDailyList", "closingPrices", "data"]:
            if key in raw and isinstance(raw[key], list):
                return raw[key]

    return []


def fetch_daily_history(ins_code: str, limit: int = 120) -> List[Dict]:
    """
    تاریخچه روزانه بر اساس insCode.
    خروجی: لیست مرتب‌شده از قدیمی به جدید، حداکثر `limit` روز آخر.
    """
    url = DAILY_URL_TEMPLATE.format(ins_code=ins_code)
    resp = session.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        },
    )
    resp.raise_for_status()
    raw = resp.json()
    items = _extract_daily_items(raw)

    # سورت بر اساس dEven از قدیمی به جدید
    def _get_date_int(rec):
        try:
            return int(rec.get("dEven", 0))
        except Exception:
            return 0

    items_sorted = sorted(items, key=_get_date_int)

    # فقط آخرین n تا
    if limit and limit > 0:
        items_sorted = items_sorted[-limit:]

    history: List[Dict] = []
    for it in items_sorted:
        d_raw = it.get("dEven")
        d_str = str(d_raw) if d_raw is not None else ""
        if len(d_str) == 8:
            # فرم 20251125
            date_jalali = f"{d_str[0:4]}/{d_str[4:6]}/{d_str[6:8]}"
        else:
            date_jalali = d_str

        try:
            close = float(it.get("pClosing", 0) or 0)
        except Exception:
            close = 0.0

        try:
            volume = float(it.get("qTotTran5J", 0) or 0)
        except Exception:
            volume = 0.0

        history.append(
            {
                "date": date_jalali,
                "close": close,
                "volume": volume,
                "raw": it,
            }
        )

    return history


def get_history_for_symbol(symbol: str, limit: int = 120) -> List[Dict]:
    """
    گرفتن تاریخچه قیمت یک نماد بر اساس اسم نماد.
    """
    ins_code = get_inscode_for_symbol(symbol)
    if not ins_code:
        return []
    return fetch_daily_history(ins_code, limit=limit)


if __name__ == "__main__":
    sym = "فملی"
    print(f"Testing history for {sym} ...")
    hist = get_history_for_symbol(sym, limit=10)
    print(f"Records: {len(hist)}")
    for row in hist:
        print(row["date"], row["close"], row["volume"])
