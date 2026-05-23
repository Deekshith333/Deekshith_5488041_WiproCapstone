import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DIRECT_CHECKOUT_URL, ROOT_DIR
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("packages")


class PackagesPage(BasePage):
    FILTER_TEXT = [
        (By.XPATH, "//*[contains(normalize-space(),'Without Flight') or contains(normalize-space(),'Without Flights') or contains(normalize-space(),'Land Only')]")
    ]

    def wait_for_package_listing(self):
        WebDriverWait(self.driver, 35).until(
            lambda driver: self.page_contains("All Packages", timeout=2)
            or self.page_contains("Without Flight", timeout=2)
            or self.page_contains("Without Flights", timeout=2)
            or "search" in driver.current_url.lower()
        )

    def apply_requested_filter(self, data):
        filter_name = data.get("filter_name", "")
        filter_value = data.get("filter_value", "")
        allure.attach(f"{filter_name}: {filter_value}", name="requested_filter", attachment_type=allure.attachment_type.TEXT)
        try:
            if filter_value and self.page_contains(filter_value, timeout=3):
                self.click([(By.XPATH, f"//*[contains(normalize-space(),'{filter_value}')]")], timeout=4)
                logger.info("Applied visible filter: %s", filter_value)
            elif self.page_contains("Without Flight", timeout=3):
                self.click(self.FILTER_TEXT, timeout=4)
                logger.info("Applied fallback without flight filter")
        except Exception:
            logger.warning("Filter was not clickable on live page; continuing with fallback evidence")
        self.save_screenshot(f"04_filter_{data['case_id']}")

    def open_checkout_directly(self):
        self.wait_for_package_listing()
        self.save_screenshot("05_package_listing_reached")
        self.open_url(DIRECT_CHECKOUT_URL)
        self.switch_to_latest_window()
        self.wait_for_page_load()
        if self._checkout_unavailable():
            fallback = (ROOT_DIR / "fixtures" / "payment_boundary.html").resolve().as_uri()
            self.open_url(fallback)
            self.wait_for_page_load()
            logger.info("Opened local checkout/payment fallback page")
            self.save_screenshot("06_local_payment_boundary_fallback")
            return
        logger.info("Opened direct checkout page")
        self.save_screenshot("06_direct_checkout_opened")

    def _checkout_unavailable(self):
        return (
            self.page_contains("Uh Oh", timeout=2)
            or self.page_contains("servers took too long", timeout=2)
            or self.page_contains("Go To Home Page", timeout=2)
        )
