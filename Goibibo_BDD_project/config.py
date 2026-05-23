from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent

BASE_URL = "https://www.goibibo.com"
HOLIDAYS_HOME_URL = "https://giholidays.makemytrip.com/holidays-india/"
HOLIDAYS_SEARCH_URL = "https://giholidays.makemytrip.com/holidays/india/search"
DIRECT_CHECKOUT_URL = "https://giholidays.makemytrip.com/checkout/?id=1634717750584158"

DEFAULT_TIMEOUT = 25
STEP_DELAY = 1.6

SCREENSHOT_DIR = ROOT_DIR / "screenshots"
LOG_DIR = ROOT_DIR / "logs"
REPORT_DIR = ROOT_DIR / "reports"
ALLURE_RESULTS_DIR = REPORT_DIR / "allure-results"
ALLURE_REPORT_DIR = REPORT_DIR / "allure-report"
JUNIT_REPORT_DIR = REPORT_DIR / "junit"
JSON_REPORT = REPORT_DIR / "behave_report.json"
LOCAL_HOME_PAGE = (ROOT_DIR / "fixtures" / "goibibo_homepage.html").resolve().as_uri()
LOCAL_HOLIDAYS_PAGE = (ROOT_DIR / "fixtures" / "holidays_search.html").resolve().as_uri()
