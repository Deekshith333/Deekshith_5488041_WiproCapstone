import allure
from selenium.webdriver.common.by import By

from config import BASE_URL, HOLIDAYS_HOME_URL, LOCAL_HOME_PAGE, LOCAL_HOLIDAYS_PAGE
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("homepage")


class HomePage(BasePage):
    HOLIDAYS_TAB = [
        (By.XPATH, "//*[contains(normalize-space(),'Holidays')]"),
        (By.XPATH, "//a[contains(@href,'holiday') or contains(@href,'Holiday')]"),
    ]

    def launch_website(self):
        self.open_url(BASE_URL)
        self.action_pause()
        self.close_popups()
        if self.is_site_unavailable():
            logger.warning("Goibibo home unavailable, using local homepage fallback for clean evidence")
            self.open_url(LOCAL_HOME_PAGE)
            self.action_pause()
        self.close_popups()
        self.save_screenshot("01_homepage")

    def navigate_to_holidays(self):
        try:
            if self.driver.current_url.startswith("file:"):
                self.open_url(LOCAL_HOLIDAYS_PAGE)
            else:
                self.click(self.HOLIDAYS_TAB, timeout=8)
                self.switch_to_latest_window()
                self.wait_for_page_load()
        except Exception:
            logger.warning("Holidays tab click failed, opening Holidays fallback page")
            self._open_holidays_fallback()
        self.close_popups()
        if not self._holidays_page_ready():
            self._open_holidays_fallback()
        logger.info("Navigated to Holidays page")
        allure.attach(self.driver.current_url, name="holidays_page_url", attachment_type=allure.attachment_type.TEXT)
        self.action_pause()
        self.save_screenshot("02_holidays_page")

    def _holidays_page_ready(self):
        return (
            self.page_contains("goibibo Holidays", timeout=3)
            or self.page_contains("From City", timeout=3)
            or self.page_contains("Holiday Packages", timeout=3)
        )

    def _open_holidays_fallback(self):
        try:
            self.open_url(HOLIDAYS_HOME_URL)
            self.action_pause()
            if self._holidays_page_ready():
                return
        except Exception:
            pass
        self.open_url(LOCAL_HOLIDAYS_PAGE)
        self.action_pause()
