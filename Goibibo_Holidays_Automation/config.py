from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

BASE_URL = "https://www.goibibo.com"
HOLIDAYS_FALLBACK_URL = "https://www.goibibo.com/holidays/"
GI_HOLIDAYS_HOME_URL = "https://giholidays.makemytrip.com/holidays-india/"
HOLIDAYS_SEARCH_URL = "https://giholidays.makemytrip.com/holidays/india/search"
DIRECT_CHECKOUT_URL = "https://giholidays.makemytrip.com/checkout/?id=1634717750584158"

DEFAULT_TIMEOUT = 25

SCREENSHOT_DIR = ROOT_DIR / "screenshots"
LOG_DIR = ROOT_DIR / "logs"
REPORT_DIR = ROOT_DIR / "reports"
