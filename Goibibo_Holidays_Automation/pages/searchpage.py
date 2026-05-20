from urllib.parse import urlencode

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from config import HOLIDAYS_SEARCH_URL
from pages.base_page import BasePage


class SearchPage(BasePage):
    FROM_CITY = [
        (By.XPATH, "//*[contains(normalize-space(),'From City')]"),
    ]
    TO_CITY = [
        (By.XPATH, "//*[contains(normalize-space(),'To City') or contains(normalize-space(),'Country')]"),
    ]
    DATE = [
        (By.XPATH, "//*[normalize-space()='Select Date']"),
        (By.XPATH, "//*[contains(normalize-space(),'Departure Date')]"),
        (By.XPATH, "//*[contains(normalize-space(),'Starting Date')]"),
    ]
    ROOMS_GUESTS = [
        (By.XPATH, "//*[normalize-space()='Select Rooms']"),
        (By.XPATH, "//*[contains(normalize-space(),'Rooms & Guests')]"),
    ]
    SEARCH = [
        (By.XPATH, "//button[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'SEARCH')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'SEARCH')]"),
    ]
    INPUT = [
        (By.XPATH, "//input[not(@type='hidden')]"),
        (By.XPATH, "//*[@contenteditable='true']"),
    ]
    MONTHS = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }

    def enter_search_details(self, data):
        try:
            self._select_city(self.FROM_CITY, data["from_city"])
            self._select_city(self.TO_CITY, data["to_city"])
            self._select_date(data["departure_day"], data["departure_month"], data["departure_year"])
            self._apply_guests_if_open(data["rooms"], data["adults"])
            self.click(self.SEARCH, timeout=12)
            self.switch_to_latest_window()
            self._wait_for_results()
        except Exception:
            self.save_screenshot("search_widget_failed_using_direct_url")
            self.open_results_directly(data)

        self.save_screenshot("03_package_listing")

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

    def _select_city(self, field, city):
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

    def _select_date(self, day, month, year):
        self.js_click_visible(self.DATE, timeout=8)
        day_number = str(int(day))
        try:
            self.click(
                [
                    (By.XPATH, f"//*[contains(@aria-label,'{day_number}') and contains(@aria-label,'{month}') and contains(@aria-label,'{year}')]"),
                    (By.XPATH, f"//*[@role='button' and normalize-space()='{day_number}']"),
                    (By.XPATH, f"//*[contains(@class,'Calendar') or contains(@class,'calendar') or contains(@class,'DayPicker')]//*[normalize-space()='{day_number}']"),
                    (By.XPATH, f"//button[normalize-space()='{day_number}' and not(@disabled)]"),
                ],
                timeout=8,
            )
        except Exception:
            self.driver.switch_to.active_element.send_keys(Keys.ESCAPE)
            raise

    def _apply_guests_if_open(self, rooms, adults):
        if self.page_contains(f"{adults} Adult", timeout=2):
            return
        try:
            self.js_click_visible(self.ROOMS_GUESTS, timeout=5)
            for label in ["APPLY", "Apply", "DONE", "Done"]:
                if self.page_contains(label, timeout=2):
                    self.click_text(label, timeout=4)
                    return
        except Exception:
            return

    def _wait_for_results(self):
        WebDriverWait(self.driver, 35).until(
            lambda driver: self.page_contains("All Packages", timeout=2)
            or self.page_contains("Without Flight", timeout=2)
            or self.page_contains("Without Flights", timeout=2)
            or "search" in driver.current_url.lower()
        )

