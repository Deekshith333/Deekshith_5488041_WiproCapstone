from pathlib import Path
from typing import Iterable

import pytest
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT, SCREENSHOT_DIR

Locator = tuple[str, str]


class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def open_url(self, url: str):
        self.driver.get(url)
        self.wait_for_page_load()

    def wait_for_page_load(self):
        WebDriverWait(self.driver, self.timeout).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )

    def switch_to_latest_window(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def find_visible(self, locators: Iterable[Locator], timeout: int | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        last_error = None
        for locator in locators:
            try:
                return wait.until(EC.visibility_of_element_located(locator))
            except TimeoutException as exc:
                last_error = exc
        raise TimeoutException(f"No visible element found for locators: {list(locators)}") from last_error

    def find_clickable(self, locators: Iterable[Locator], timeout: int | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        last_error = None
        for locator in locators:
            try:
                return wait.until(EC.element_to_be_clickable(locator))
            except TimeoutException as exc:
                last_error = exc
        raise TimeoutException(f"No clickable element found for locators: {list(locators)}") from last_error

    def click(self, locators: Iterable[Locator], timeout: int | None = None):
        element = self.find_clickable(locators, timeout)
        self.scroll_to(element)
        try:
            element.click()
        except WebDriverException:
            self.driver.execute_script("arguments[0].click();", element)

    def js_click_visible(self, locators: Iterable[Locator], timeout: int | None = None):
        element = self.find_visible(locators, timeout)
        self.scroll_to(element)
        self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locators: Iterable[Locator], value: str, clear: bool = True, timeout: int | None = None):
        element = self._find_interactable(locators, timeout)
        self.scroll_to(element)
        try:
            element.click()
            if clear:
                element.send_keys(Keys.CONTROL, "a")
                element.send_keys(Keys.BACKSPACE)
            element.send_keys(value)
        except WebDriverException:
            self.driver.execute_script("arguments[0].focus();", element)
            if clear:
                self.driver.execute_script("arguments[0].value = '';", element)
            element.send_keys(value)

    def type_if_present(self, locators: Iterable[Locator], value: str, timeout: int = 5) -> bool:
        try:
            self.type_text(locators, value, timeout=timeout)
            return True
        except Exception:
            return False

    def type_active_or_first(self, locators: Iterable[Locator], value: str):
        active = self.driver.switch_to.active_element
        tag = (active.tag_name or "").lower()
        editable = tag in {"input", "textarea"} or active.get_attribute("contenteditable") == "true"
        if editable and self._is_interactable(active):
            active.send_keys(Keys.CONTROL, "a")
            active.send_keys(Keys.BACKSPACE)
            active.send_keys(value)
            return
        self.type_text(locators, value)

    def click_text(self, text: str, timeout: int | None = None):
        self.click([(By.XPATH, f"//*[contains(normalize-space(),'{text}')]")], timeout=timeout)

    def page_contains(self, text: str, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, f"//*[contains(normalize-space(),'{text}')]"))
            )
            return True
        except TimeoutException:
            return False

    def scroll_to(self, element: WebElement):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)

    def save_screenshot(self, name: str) -> Path:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        path = SCREENSHOT_DIR / f"{name}.png"
        self.driver.save_screenshot(str(path))
        return path

    def close_popups(self):
        locators = [
            (By.XPATH, "//*[contains(@class,'close') or contains(@class,'Close')]"),
            (By.XPATH, "//*[normalize-space()='×' or normalize-space()='x' or normalize-space()='X']"),
            (By.XPATH, "//*[contains(normalize-space(),'Skip') or contains(normalize-space(),'Later')]"),
            (By.XPATH, "//*[contains(normalize-space(),'Not now') or contains(normalize-space(),'No thanks')]"),
        ]
        for locator in locators:
            for element in self.driver.find_elements(*locator)[:5]:
                try:
                    if element.is_displayed():
                        self.driver.execute_script("arguments[0].click();", element)
                except WebDriverException:
                    continue

    def is_site_unavailable(self) -> bool:
        body = self.driver.find_element(By.TAG_NAME, "body").text.lower()
        title = self.driver.title.lower()
        unavailable = [
            "503 service temporarily unavailable",
            "err_http2_protocol_error",
            "this site can't be reached",
            "this page isn't working",
            "dns_probe",
            "server ip address could not be found",
        ]
        return any(text in body or text in title for text in unavailable)

    def skip_if_site_unavailable(self):
        if self.is_site_unavailable():
            pytest.skip("Goibibo site is unavailable or returned a browser/network error.")

    def _find_interactable(self, locators: Iterable[Locator], timeout: int | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        locator_list = list(locators)

        def _predicate(driver):
            for locator in locator_list:
                for element in driver.find_elements(*locator):
                    if self._is_interactable(element):
                        return element
            return False

        return wait.until(_predicate, message=f"No interactable element found for locators: {locator_list}")

    def _is_interactable(self, element: WebElement) -> bool:
        try:
            rect = element.rect
            return (
                element.is_displayed()
                and element.is_enabled()
                and rect.get("width", 0) > 0
                and rect.get("height", 0) > 0
                and not element.get_attribute("disabled")
                and not element.get_attribute("readonly")
            )
        except WebDriverException:
            return False
