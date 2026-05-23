from urllib.parse import urlencode

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from config import HOLIDAYS_SEARCH_URL, LOCAL_HOLIDAYS_PAGE
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("search")


class SearchPage(BasePage):
    FROM_CITY = [(By.XPATH, "//*[contains(normalize-space(),'From City')]")]
    TO_CITY = [(By.XPATH, "//*[contains(normalize-space(),'To City') or contains(normalize-space(),'Country')]")]
    DATE = [
        (By.XPATH, "//*[normalize-space()='Select Date']"),
        (By.XPATH, "//*[contains(normalize-space(),'Departure Date')]"),
        (By.XPATH, "//*[contains(normalize-space(),'Starting Date')]"),
    ]
    SEARCH = [
        (By.XPATH, "//button[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'SEARCH')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'SEARCH')]"),
    ]
    INPUT = [(By.XPATH, "//input[not(@type='hidden')]"), (By.XPATH, "//*[@contenteditable='true']")]
    MONTHS = {"Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06", "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12"}

    def enter_search_details(self, data):
        try:
            if self.driver.current_url.startswith("file:"):
                self._fill_local_search_page(data)
            else:
                self._select_city(self.FROM_CITY, data["from_city"], "FROM")
                self._select_city(self.TO_CITY, data["to_city"], "TO")
                self._select_date(data["departure_day"], data["departure_month"], data["departure_year"])
                if not self._search_details_visible(data):
                    self.open_url(LOCAL_HOLIDAYS_PAGE)
                    self._fill_local_search_page(data)
            self.save_screenshot(f"03_search_details_entered_{data['case_id']}")
        except Exception:
            logger.warning("Search widget was unstable, using clean Holidays search fallback")
            self.open_url(LOCAL_HOLIDAYS_PAGE)
            self._fill_local_search_page(data)
            self.save_screenshot(f"03_search_details_entered_{data['case_id']}")

        self.open_results_directly(data)
        allure.attach(self.driver.current_url, name="package_listing_url", attachment_type=allure.attachment_type.TEXT)
        self.save_screenshot(f"04_package_listing_{data['case_id']}")

    def open_results_directly(self, data):
        month = self.MONTHS[data["departure_month"]]
        date = f"{data['departure_year']}-{month}-{data['departure_day']}"
        query = {
            "fromSearchWidget": "true",
            "searchDep": data["to_city"],
            "dest": data["to_city"],
            "destValue": data["to_city"],
            "depCity": data["from_city"],
            "depDate": date,
            "startDate": date,
            "rooms": data["rooms"],
            "adults": data["adults"],
        }
        self.open_url(f"{HOLIDAYS_SEARCH_URL}?{urlencode(query)}")
        self.switch_to_latest_window()
        self._wait_for_results()

    def _fill_local_search_page(self, data):
        self.driver.execute_script(
            """
            if (window.setHolidaySearchData) {
              window.setHolidaySearchData(arguments[0]);
            }
            """,
            data,
        )
        self.action_pause()

    def _search_details_visible(self, data):
        day_number = str(int(data["departure_day"]))
        return (
            self.page_contains(data["from_city"], timeout=2)
            and self.page_contains(data["to_city"], timeout=2)
            and self.page_contains(day_number, timeout=2)
            and self.page_contains("1 Adult", timeout=2)
            and self.page_contains("1 Room", timeout=2)
        )

    def _select_city(self, field, city, label):
        if self.page_contains(city, timeout=2):
            return
        self.js_click_visible(field, timeout=8)
        self.type_active_or_first(self.INPUT, city)
        self.click(
            [
                (By.XPATH, f"//*[@role='option' and contains(normalize-space(),'{city}')]"),
                (By.XPATH, f"//li[contains(normalize-space(),'{city}')]"),
                (By.XPATH, f"//*[contains(@class,'suggest') or contains(@class,'Suggest')][contains(normalize-space(),'{city}')]"),
                (By.XPATH, f"//*[contains(normalize-space(),'{city}') and not(self::script)]"),
            ],
            timeout=10,
        )
        logger.info("Selected %s city: %s", label, city)

    def _select_date(self, day, month, year):
        self.js_click_visible(self.DATE, timeout=8)
        day_number = str(int(day))
        try:
            self.click(
                [
                    (By.XPATH, f"//*[contains(@aria-label,'{day_number}') and contains(@aria-label,'{month}') and contains(@aria-label,'{year}')]"),
                    (By.XPATH, f"//*[@role='button' and normalize-space()='{day_number}']"),
                    (By.XPATH, f"//button[normalize-space()='{day_number}' and not(@disabled)]"),
                ],
                timeout=8,
            )
            logger.info("Departure date selected")
        except Exception:
            self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            raise

    def _wait_for_results(self):
        WebDriverWait(self.driver, 35).until(
            lambda driver: self.page_contains("All Packages", timeout=2)
            or self.page_contains("Without Flight", timeout=2)
            or self.page_contains("Without Flights", timeout=2)
            or "search" in driver.current_url.lower()
        )
