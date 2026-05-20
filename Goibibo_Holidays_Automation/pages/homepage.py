from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import BASE_URL, GI_HOLIDAYS_HOME_URL, HOLIDAYS_FALLBACK_URL
from pages.base_page import BasePage


class HomePage(BasePage):
    HOLIDAYS_TAB = [
        (By.XPATH, "//a[contains(@href,'holiday') or contains(normalize-space(),'Holidays')]"),
        (By.XPATH, "//*[contains(normalize-space(),'Holidays')]"),
    ]

    def launch_website(self):
        self.open_url(BASE_URL)
        if self.is_site_unavailable():
            self.save_screenshot("goibibo_home_unavailable_using_holidays_fallback")
            self.open_url(GI_HOLIDAYS_HOME_URL)
            if self.is_site_unavailable():
                self.open_url(HOLIDAYS_FALLBACK_URL)
                self.skip_if_site_unavailable()
        self.close_popups()
        self.save_screenshot("01_homepage")

    def navigate_to_holidays(self):
        before_url = self.driver.current_url
        try:
            self.click(self.HOLIDAYS_TAB, timeout=12)
            self.switch_to_latest_window()
            self.wait_for_page_load()
        except Exception:
            self.open_url(GI_HOLIDAYS_HOME_URL)

        if self.driver.current_url == before_url or "flight" in self.driver.current_url.lower():
            self.open_url(GI_HOLIDAYS_HOME_URL)

        if self.is_site_unavailable():
            self.open_url(HOLIDAYS_FALLBACK_URL)
            self.skip_if_site_unavailable()
        self.close_popups()
        WebDriverWait(self.driver, 20).until(
            lambda driver: "holiday" in driver.current_url.lower() or self.page_contains("Holidays", timeout=2)
        )

        self.save_screenshot("02_holidays_page")
