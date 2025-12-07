# api/main.py
import os
import requests
import unicodedata
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", "60"))

USE_PROXY_TSETMC = os.getenv("USE_PROXY_TSETMC", "False").lower() == "true"
PROXY_TSETMC = os.getenv("PROXY_TSETMC", "")

OFFLINE_DEV_MODE = os.getenv("OFFLINE_DEV_MODE", "False").lower() == "true"
#یه سشن مشترک برای همه درخواست ها 
session = requests.Session()

if USE_PROXY_TSETMC and PROXY_TSETMC:
    session.proxies.update({
        "http": PROXY_TSETMC,
        "https": PROXY_TSETMC,
    })
    print(f"[TSETMC] Using proxy: {PROXY_TSETMC}")
else:
    print("[TSETMC] Not using proxy (direct connection).")

# market map API (TSETMC)
API_URL = (
    "http://cdn.tsetmc.com/api/ClosingPrice/"
    "GetMarketMap?market=0&size=1360&sector=0&typeSelected=1"
)

# گه از پروکسی محیط استفاده نکنه
session.trust_env = False
#session.proxies = {"http": None, "https": None}
#for SSL error
#session.verify = False
#resp = session.get(url, timeout=60, verify=False)



def normalize_symbol(symbol: str) -> str:
    """
    نرمال‌سازی نماد/نام فارسی برای مقایسه مطمئن‌تر.

    کارهایی که انجام می‌شود:
    - اگر مقدار None یا خالی باشد، رشته خالی برمی‌گرداند.
    - تبدیل ورودی به رشته و حذف فاصله‌های ابتدا و انتها.
    - یکسان‌سازی حروف عربی/فارسی (ي → ی ، ك → ک).
    - حذف فاصله وسط متن و نیم‌فاصله (Zero-width non-joiner).
    - نرمال‌سازی یونی‌کد با NFC (برای یکدست شدن شکل حروف).

    ورودی:
        symbol: نماد یا نام فارسی که می‌خواهیم نرمال کنیم.

    خروجی:
        رشتهٔ نرمال‌شده، بدون فاصله، با حروف یک‌دست (برای مقایسه).
    """
    if not symbol:
        return ""
    s = str(symbol).strip()
    s = s.replace("ي", "ی").replace("ك", "ک")
    s = s.replace(" ", "").replace("\u200c", "")
    s = unicodedata.normalize("NFC", s)
    return s


def fetch_market_map(
    url: str | None = None,
    retries: int = 3,
):
    """
    گرفتن نقشهٔ بازار از TSETMC با ریتری و تایم‌اوت و استفاده از session مشترک.
    اگر OFFLINE_DEV_MODE روشن باشد، بعداً می‌توانیم اینجا هم mock برگردانیم.
    """
    if url is None:
        #ترجیحاً HTTPS
        url = "https://cdn.tsetmc.com/api/ClosingPrice/GetMarketMap?market=0&size=1360&sector=0&typeSelected=1"

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, timeout=HTTP_TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last_exc = e
            print(
                f"Request failed (attempt {attempt}/{retries}): {e}. Retrying..."
            )
    # اگر بعد از همه تلاش‌ها نشد
    raise Exception(f"Failed to fetch data after {retries} retries") from last_exc


def get_stock_info(symbol: str) -> dict | None:
    """
    گرفتن اطلاعات یک نماد خاص از روی لیست Market Map.

    منطق کلی:
    - نماد ورودی را نرمال‌سازی می‌کنیم (برای مقابله با تفاوت حروف/فاصله).
    - Market Map را از API می‌گیریم (لیستی از رکوردها).
    - روی دو فیلد زیر مچ می‌کنیم:
        * کد نماد:  lVal18AFC
        * نام فارسی نماد: lVal30
    - اگر رکوردی یافت شد، از آن اطلاعات مهم مثل قیمت، درصد تغییر، حجم، ارزش
      و ... را استخراج می‌کنیم و در یک دیکشنری مرتب برمی‌گردانیم.
    - اگر نمادی پیدا نشود، None برمی‌گردانیم.

    ورودی:
        symbol: رشته‌ای که می‌تواند کد نماد یا نام فارسی نماد باشد.

    خروجی:
        یک دیکشنری شامل اطلاعات نماد، یا None اگر چیزی پیدا نشود.
    """
    #offline mode
    if OFFLINE_DEV_MODE:
        return {
            "symbol": symbol,
            "name": f"نماد تستی {symbol}",
            "sector": "فلزات اساسي",
            "last_price": 10000.0,
            "last_trade": 10100.0,
            "yesterday_price": 9800.0,
            "percent_change": 2.04,
            "percent_change_precise": 2.04,
            "volume": 12345678.0,
            "value": 987654321000.0,
            "trades": 4321.0,
            "market_cap": 250_000_000_000_000.0,
            "date": "1403/09/16",
            "time": "12:30:00",
            "last_update": "1403-09-16 12:31",
        }
    
    sym = normalize_symbol(symbol)
    if not sym:
        return None
    # گرفتن لیست کامل Market Map
    items = fetch_market_map()
    # جست‌وجوی نماد در لیست آیتم‌ها با مقایسه نرمال‌شده
    matches = [
        it
        for it in items
        if normalize_symbol(it.get("lVal18AFC", "")) == sym
        or normalize_symbol(it.get("lVal30", "")) == sym
    ]

    if not matches:
        return None
    
    # فعلا اولین مچ را به عنوان رکورد مرجع استفاده می‌کنیم
    rec = matches[0]

    def get_float(key: str, default: float = 0.0) -> float:
        """
        تابع کمکی برای تبدیل مقدار یک کلید از رکورد به float.

        اگر مقدار قابل تبدیل نباشد (None، رشتهٔ خالی، مقدار نامعتبر)،
        مقدار پیش‌فرض را برمی‌گرداند.
        """
        try:
            return float(rec.get(key, default) or 0.0)
        except (TypeError, ValueError):
            return default
        
    # مقادیر پایه‌ای نماد
    symbol_val = rec.get("lVal18AFC", sym)
    name = rec.get("lVal30", sym)
    sector = rec.get("lSecVal", "")

    # قیمت‌ها و درصد تغییر
    last_price = get_float("pClosing")
    last_trade = get_float("pDrCotVal")
    yesterday_price = get_float("priceYesterday")
    percent = get_float("percent")
    percent_precise = get_float("priceChangePercent")

    # حجم، ارزش معاملات، تعداد، ارزش بازار
    volume = get_float("qTotTran5J")
    value = get_float("qTotCap")
    trades = get_float("zTotTran")
    market_cap = get_float("marketCap")

    # تاریخ و زمان سامانه
    time_str = rec.get("hEvenShow", "")
    date_raw = rec.get("dEven", None)

    # تبدیل عدد خام تاریخ به قالب YYYY/MM/DD اگر طولش ۸ رقم باشد (مثلا 20251126)
    date_str = str(date_raw) if date_raw is not None else ""
    if len(date_str) == 8:
        # شکل 20251126
        jalali_date = f"{date_str[0:4]}/{date_str[4:6]}/{date_str[6:8]}"
    else:
        jalali_date = str(date_raw)

    # دیکشنری نهایی اطلاعات نماد
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
        # زمان به‌روزرسانی از دید ربات (لحظه‌ای که تابع را صدا زدیم)
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    return info


def format_stock_message(info: dict | None) -> str:
    """
    تبدیل دیکشنری اطلاعات نماد به یک متن فارسی برای تلگرام.

    منطق کلی:
    - اگر info خالی/None باشد، پیام «یافت نشد» برمی‌گردانیم.
    - اعداد را تا حد ممکن به صورت فرمت‌شده با جداکنندهٔ هزارگان نمایش می‌دهیم.
    - بر اساس مثبت/منفی بودن درصد تغییر، یک ایموجی (فلش/قلب) انتخاب می‌کنیم.
    - متن را خط به خط می‌سازیم و در نهایت با \\n به هم join می‌کنیم.

    ورودی:
        info: دیکشنری برگشتی از get_stock_info

    خروجی:
        یک رشتهٔ چندخطی آماده برای ارسال در چت تلگرام.
    """
    if not info:
        return "نتوانستم اطلاعاتي براي اين نماد پيدا کنم."

    def fmt_int(x):
        """تبدیل مقدار ورودی به عدد صحیح با جداکننده هزارگان، در صورت امکان."""

        try:
            return f"{int(x):,}"
        except Exception:
            return str(x)
    # مقادیر اصلی نماد
    sym = info["symbol"]
    name = info["name"]
    sector = info.get("sector", "")
    # قیمت‌ها و درصد تغییر
    lp = info["last_price"]
    lt = info["last_trade"]
    yp = info["yesterday_price"]
    pc = info["percent_change"]
    pcp = info["percent_change_precise"]
    # حجم، ارزش، تعداد معاملات، ارزش بازار
    vol = info["volume"]
    val = info["value"]
    trades = info["trades"]
    mcap = info["market_cap"]
    # تاریخ و زمان
    d = info.get("date", "")
    t = info.get("time", "")
    upd = info.get("last_update", "")

    arrow = "💚" if pc > 0 else ("❤️" if pc < 0 else "🤍")

    lines = []
    lines.append(f"نماد: {sym}")
    lines.append(f"نام: {name}")
    if sector:
        lines.append(f"گروه صنعت: {sector}")

    lines.append("")
    lines.append(f"{arrow} تغيير امروز: {pc:+.2f}% (دقيق‌تر: {pcp:+.2f}%)")
    lines.append(f"قيمت پاياني: {fmt_int(lp)} ريال")
    lines.append(f"آخرين معامله: {fmt_int(lt)} ريال")
    lines.append(f"قيمت ديروز: {fmt_int(yp)} ريال")

    lines.append("")
    lines.append(f"حجم معاملات: {fmt_int(vol)} سهم")
    lines.append(f"ارزش معاملات: {fmt_int(val)} ريال")
    lines.append(f"تعداد معاملات: {fmt_int(trades)}")
    lines.append(f"ارزش بازار تقريبي: {fmt_int(mcap)}")

    lines.append("")
    lines.append(f"تاريخ سامانه: {d} - ساعت: {t}")
    lines.append(f"زمان به‌روزرسانی ربات: {upd}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Testing api.main with symbol 'فملی' ...")
    info = get_stock_info("فملی")
    print("Raw info dict:")
    print(info)
    print("\nFormatted message:")
    print(format_stock_message(info))
