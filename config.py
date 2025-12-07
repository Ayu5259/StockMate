import os
from dotenv import load_dotenv

load_dotenv()

def str_to_bool(x: str) -> bool:
    return x.strip().lower() in ("1", "true", "yes", "on")

#  تلگرام
PROXY_TELEGRAM = os.getenv("PROXY_TELEGRAM") or None
TELEGRAM_PROXY_ENABLED = str_to_bool(os.getenv("TELEGRAM_PROXY_ENABLED", "false"))

# TSETMC
USE_PROXY_TSETMC = str_to_bool(os.getenv("USE_PROXY_TSETMC", "false"))
PROXY_TSETMC = os.getenv("PROXY_TSETMC") if USE_PROXY_TSETMC else None
