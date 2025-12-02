"""
این فایل مسئول جمع‌آوری اطلاعات اولیه از سایت TSETMC 
و انجام پردازش‌های پایه‌ای مانند دریافت داده‌ها برای نمادهای بورس است.
"""
import requests
import unicodedata
from datetime import datetime
from requests.exceptions import RequestException

API_URL = "http://cdn.tsetmc.com/api/ClosingPrice/GetMarketMap?market=0&size=1360&sector=0&typeSelected=1"

session = requests.Session()
session.trust_env = False
session.proxies = {"http": None, "https": None}


def normalize_symbol(symbol: str) -> str:
    """Normalize symbol or name: strip, remove spaces, unify Arabic/Persian forms."""
    if not symbol:
        return ""
    s = str(symbol).strip()
    # یکسان سازی حروف عربی و فارسی
    s = (
        s.replace("ي", "ی")
         .replace("ي", "ی")
         .replace("ك", "ک")
         .replace("ك", "ک")
    )
    # حذف فاصله ها
    s = s.replace(" ", "")
    return s



import time
import requests

def fetch_market_map(url, retries=5):
    attempt = 0
    while attempt < retries:
        try:
            resp = session.get(url, timeout=120)
            resp.raise_for_status()
            return resp.json()  
        except requests.exceptions.RequestException as e:
            attempt += 1
            print(f"Request failed: {e}. Retrying {attempt}/{retries}...")
            if attempt == retries:
                raise Exception(f"Failed to fetch data after {retries} retries")


def get_stock_info(symbol: str) -> dict | None:
    sym = normalize_symbol(symbol)
    if not sym:
        return None

    items = fetch_market_map("http://cdn.tsetmc.com/api/ClosingPrice/GetMarketMap?market=0&size=1360&sector=0&typeSelected=1")("http://cdn.tsetmc.com/api/ClosingPrice/GetMarketMap?market=0&size=1360&sector=0&typeSelected=1")()

    # 1) مچ دقیق
    exact_matches = []
    for it in items:
        code_norm = normalize_symbol(it.get("lVal18AFC", ""))
        name_norm = normalize_symbol(it.get("lVal30", ""))
        if sym == code_norm or sym == name_norm:
            exact_matches.append(it)

    if exact_matches:
        rec = exact_matches[0]
    else:
        # 2) مچ تقریبی روی نام
        fuzzy_matches = []
        for it in items:
            name_norm = normalize_symbol(it.get("lVal30", ""))
            if sym in name_norm or name_norm.startswith(sym):
                fuzzy_matches.append(it)
        if not fuzzy_matches:
            return None
        rec = fuzzy_matches[0]

    # باقی کد همون چیزی باشه که الان داری:
    #  get_float, ساختن دیکشنری info و ...


    def get_float(key: str, default: float = 0.0) -> float:
        try:
            return float(rec.get(key, default) or 0.0)
        except (TypeError, ValueError):
            return default

    symbol_val = rec.get("lVal18AFC", sym)
    name = rec.get("lVal30", sym)
    sector = rec.get("lSecVal", "")

    last_price = get_float("pClosing")
    last_trade = get_float("pDrCotVal")
    yesterday_price = get_float("priceYesterday")
    percent = get_float("percent")
    percent_precise = get_float("priceChangePercent")

    volume = get_float("qTotTran5J")
    value = get_float("qTotCap")
    trades = get_float("zTotTran")

    # تعداد سهام منتشرشده (اين کليد در خروجي مارکت‌مپ وجود دارد در خيلي از نمادها)
    shares_outstanding = get_float("zTitad")

    # اگر تعداد سهام در دسترس بود، مارکت‌کپ = قيمت پاياني × تعداد سهام
    if shares_outstanding > 0 and last_price > 0:
        market_cap = last_price * shares_outstanding
    else:
        # اگر نبود، صفر مي‌گذاريم فعلا
        market_cap = 0.0


    time_str = rec.get("hEvenShow", "")
    date_raw = rec.get("dEven", None)

    date_str = str(date_raw) if date_raw is not None else ""
    if len(date_str) == 8:
        jalali_date = f"{date_str[0:4]}/{date_str[4:6]}/{date_str[6:8]}"
    else:
        jalali_date = str(date_raw)

    info = {
        "symbol": symbol_val,
        "name": name,
        "sector": sector,
        "last_price": last_price,
        "last_trade": last_trade,
        "yesterday_price": yesterday_price,
        "percent_change": percent,
        "percent_change_precise": percent_precise,
        "volume": volume,
        "value": value,
        "trades": trades,
        "market_cap": market_cap,
        "date": jalali_date,
        "time": time_str,
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    return info

def build_simple_analysis(info: dict) -> str:
    """Generate a very simple textual summary based on today's change and volume."""
    pc = info.get("percent_change", 0.0) or 0.0
    vol = info.get("volume", 0.0) or 0.0
    val = info.get("value", 0.0) or 0.0

    # تحليل جهت حرکت
    if pc >= 5:
        trend_text = "امروز رشد قوی و پر رنگی داشته است."
    elif 2 <= pc < 5:
        trend_text = "امروز در محدوده مثبت و با رشد قابل توجه معامله شده است."
    elif 0.1 <= pc < 2:
        trend_text = "امروز کمی مثبت بوده و روند ملايمی داشته است."
    elif -0.1 < pc < 0.1:
        trend_text = "امروز تقريبا بدون تغيير بوده است."
    elif -2 < pc <= -0.1:
        trend_text = "امروز کمی منفی بوده و فشار فروش سبک بوده است."
    elif -5 < pc <= -2:
        trend_text = "امروز افت قابل ملاحظه ای داشته است."
    else:  # pc <= -5
        trend_text = "امروز افت شديدی را تجربه کرده است."

    # تحليل خيلي ساده حجم/ارزش (صرفا بر اساس عدد خام، نه ميانگين تاريخي)
    if val >= 1_000_000_000_000:  # حدود ١٠^١٢ ريال
        volume_text = "حجم و ارزش معاملات امروز بالا و جلب توجه بوده است."
    elif val >= 100_000_000_000:
        volume_text = "حجم و ارزش معاملات امروز در حد متوسط رو به بالا بوده است."
    elif val > 0:
        volume_text = "حجم و ارزش معاملات امروز پايين بوده و توجه زيادي به سهم نشده است."
    else:
        volume_text = "اطلاعات دقيقی از حجم و ارزش معاملات در دسترس نيست."

    return f"جمع بندي امروز: سهم {trend_text} همچنين {volume_text}"

def format_stock_message(info: dict | None) -> str:
    """Convert stock info dict to a Farsi message for Telegram."""

    if not info:
        return "نتوانستم اطلاعاتی براي اين نماد پيدا کنم."

    def fmt_int(x):
        try:
            return f"{int(x):,}"
        except (TypeError, ValueError):
            return "-"

    sym = info["symbol"]
    name = info["name"]
    sector = info.get("sector", "")

    lp = info["last_price"]
    lt = info["last_trade"]
    yp = info["yesterday_price"]
    pc = info["percent_change"]
    pcp = info["percent_change_precise"]

    vol = info["volume"]
    val = info["value"]
    trades = info["trades"]
    mcap = info["market_cap"]

    d = info.get("date", "")
    t = info.get("time", "")
    upd = info.get("last_update", "")

    arrow = "💚" if pc > 0 else ("❤️" if pc < 0 else "🤍")

    lines: list[str] = []

    lines.append(f"نماد: {sym}")
    lines.append(f"نام: {name}")
    if sector:
        lines.append(f"گروه صنعت: {sector}")

    lines.append("")
    lines.append(f"{arrow} تغيير امروز: {pc:+.2f}% (دقيق تر: {pcp:+.2f}%)")
    lines.append(f"قيمت پاياني: {fmt_int(lp)} ريال")
    lines.append(f"اخرين معامله: {fmt_int(lt)} ريال")
    lines.append(f"قيمت ديروز: {fmt_int(yp)} ريال")

    lines.append("")
    lines.append(f"حجم معاملات: {fmt_int(vol)} سهم")
    lines.append(f"ارزش معاملات: {fmt_int(val)} ريال")
    lines.append(f"تعداد معاملات: {fmt_int(trades)}")
    lines.append(f"ارزش بازار تقريبي: {fmt_int(mcap)}")

    lines.append("")
    lines.append(f"تاريخ سامانه: {d} - ساعت: {t}")
    lines.append(f"زمان به روزرساني ربات: {upd}")

    analysis = build_simple_analysis(info)
    if analysis:
        lines.append("")
        lines.append(analysis)

    return "\n".join(lines)




if __name__ == "__main__":
    print("Testing main.py with symbol 'وبملت' ...")
    info = get_stock_info("وبملت")
    print("Raw info dict:")
    print(info)
    print("\nFormatted message:")
    print(format_stock_message(info))
