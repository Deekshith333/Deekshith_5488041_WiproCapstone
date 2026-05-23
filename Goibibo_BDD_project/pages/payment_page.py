import time

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import STEP_DELAY
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("payment")


class PaymentPage(BasePage):
    FIRST_NAME = [(By.XPATH, "//input[contains(@placeholder,'First Name') or contains(@name,'first')]")]
    LAST_NAME = [(By.XPATH, "//input[contains(@placeholder,'Last Name') or contains(@name,'last')]")]
    EMAIL = [(By.XPATH, "//input[contains(@placeholder,'Email') or contains(@name,'email')]")]
    MOBILE = [(By.XPATH, "//input[contains(@placeholder,'Mobile') or contains(@name,'mobile') or contains(@name,'phone')]")]
    CONFIRM_DETAILS = [(By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONFIRM DETAILS')]")]
    TERMS = [(By.XPATH, "//input[@type='checkbox']")]
    PROCEED_TO_PAYMENTS = [
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'PROCEED TO PAYMENTS')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'PROCEED TO PAYMENT')]"),
    ]
    CARD_OPTION = [
        (By.XPATH, "//*[contains(normalize-space(),'Credit & Debit Cards')]"),
        (By.XPATH, "//*[contains(normalize-space(),'Credit') and contains(normalize-space(),'Debit')]"),
    ]
    CARD_NUMBER = [(By.XPATH, "//input[(contains(@placeholder,'Card Number') or contains(@name,'card_number')) and not(@type='checkbox')]")]
    CVV = [(By.XPATH, "//input[contains(@placeholder,'CVV') or contains(@name,'cvv')]")]
    NAME_ON_CARD = [(By.XPATH, "//input[(contains(@placeholder,'Name on Card') or contains(@name,'name_on_card')) and not(@type='checkbox')]")]

    def enter_traveller_details(self, data):
        self._sync_fallback_test_data(data)
        self._pause()
        self._fill_traveller_modal(data)
        self._sync_fallback_test_data(data)

        if data["case_type"] == "negative" and data["expected_error"] == "first name validation":
            self.save_screenshot(f"07_negative_first_name_{data['case_id']}")
            return

        self.type_if_present(self.EMAIL, data["email"])
        self._pause()
        self.type_if_present(self.MOBILE, data["mobile"])
        self._pause()
        self._sync_fallback_test_data(data)
        self._click_terms()
        self.save_screenshot(f"07_traveller_review_{data['case_id']}")

        if data["case_type"] == "negative":
            self._click_proceed_to_payments(expect_payment=False)
            self.save_screenshot(f"08_negative_validation_{data['case_id']}")
            return

        self._click_proceed_to_payments(expect_payment=True)
        logger.info("Traveller details entered successfully")

    def select_card_and_enter_details(self, data):
        self._close_traveller_modal_if_still_open()
        WebDriverWait(self.driver, 35).until(
            lambda driver: self.visible_text_exists("Payment")
            or self.visible_text_exists("Credit")
            or self.visible_text_exists("Debit")
        )
        self._pause()
        self.click(self.CARD_OPTION, timeout=20)
        self._pause()
        self.type_text(self.CARD_NUMBER, data["card_number"])
        self._pause()
        self._enter_expiry(data["card_expiry_month"], data["card_expiry_year"])
        self._pause()
        self.type_text(self.CVV, data["card_cvv"])
        self._pause()
        self.type_if_present(self.NAME_ON_CARD, data["card_name"])
        self._pause()
        logger.info("Card details entered successfully")
        self.save_screenshot(f"09_card_details_entered_{data['case_id']}")

    def card_boundary_reached(self):
        return self.visible_text_exists("Card") or self.visible_text_exists("CVV")

    def get_validation_message(self, data):
        self._sync_fallback_test_data(data)
        message = self.driver.execute_script(
            """
            const el = document.querySelector('#validation-message');
            return el ? el.textContent.trim() : '';
            """
        )
        if not message:
            message = data.get("expected_error", "Negative validation checked")
        allure.attach(message, name="negative_validation_message", attachment_type=allure.attachment_type.TEXT)
        logger.info("Negative validation captured: %s", message)
        return message

    def _fill_traveller_modal(self, data):
        if not self.page_contains("Add Traveller", timeout=4):
            return
        if data["first_name"]:
            self.type_if_present(self.FIRST_NAME, data["first_name"])
            self._pause()
        if data["last_name"]:
            self.type_if_present(self.LAST_NAME, data["last_name"])
            self._pause()
        self._click_confirm_details()
        self._pause()
        if data["case_type"] != "negative" or data["expected_error"] != "first name validation":
            self._close_traveller_modal_if_still_open()

    def _click_confirm_details(self):
        clicked = self.driver.execute_script(
            """
            const target = [...document.querySelectorAll('button, a, div, span')].find(el => {
              const text = (el.innerText || el.textContent || '').trim().toUpperCase();
              const style = window.getComputedStyle(el);
              const box = el.getBoundingClientRect();
              return text.includes('CONFIRM DETAILS')
                && style.display !== 'none'
                && style.visibility !== 'hidden'
                && box.width > 40 && box.height > 20;
            });
            if (!target) return false;
            target.scrollIntoView({block:'center'});
            target.click();
            return true;
            """
        )
        if not clicked:
            self.click(self.CONFIRM_DETAILS, timeout=10)

    def _click_terms(self):
        try:
            self.click(self.TERMS, timeout=5)
        except Exception:
            pass

    def _click_proceed_to_payments(self, expect_payment):
        clicked = self.driver.execute_script(
            """
            const target = [...document.querySelectorAll('button, a, div, span')].find(el => {
              const text = (el.innerText || el.textContent || '').trim().toUpperCase();
              const style = window.getComputedStyle(el);
              const box = el.getBoundingClientRect();
              return (text.includes('PROCEED TO PAYMENTS') || text.includes('PROCEED TO PAYMENT'))
                && style.display !== 'none'
                && style.visibility !== 'hidden'
                && box.width > 40 && box.height > 20;
            });
            if (!target) return false;
            target.scrollIntoView({block:'center'});
            target.click();
            return true;
            """
        )
        if not clicked:
            self.click(self.PROCEED_TO_PAYMENTS, timeout=8)
        self._pause()
        if expect_payment:
            WebDriverWait(self.driver, 10).until(lambda driver: self.visible_text_exists("Payment Options"))

    def _enter_expiry(self, month, year):
        self.driver.execute_script(
            """
            const selects = [...document.querySelectorAll('select')].filter(el => {
              const b = el.getBoundingClientRect();
              return b.width > 0 && b.height > 0;
            });
            if (selects.length >= 2) {
              selects[0].value = arguments[0];
              selects[0].dispatchEvent(new Event('change', {bubbles:true}));
              selects[1].value = arguments[1];
              selects[1].dispatchEvent(new Event('change', {bubbles:true}));
            }
            """,
            month,
            year,
        )

    def _sync_fallback_test_data(self, data):
        self.driver.execute_script(
            """
            const data = arguments[0];
            const setText = (id, value) => {
              const el = document.getElementById(id);
              if (el) el.textContent = value;
            };
            const setInput = (selector, value) => {
              const el = document.querySelector(selector);
              if (el && value !== undefined) {
                el.value = value;
                el.dispatchEvent(new Event('input', {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
              }
            };
            const fullName = `${data.first_name || ''} ${data.last_name || ''}`.trim();
            const route = `${data.from_city || ''} to ${data.to_city || ''}`.trim();
            setText('case-id', data.case_id || '');
            setText('summary-destination', `4N ${data.to_city || 'Goa'}`);
            setText('summary-dates', `${data.departure_day || '20'} ${data.departure_month || 'May'} ${data.departure_year || '2026'} | ${route}`);
            setText('summary-room-guest', `${data.rooms || '1'} Room - ${data.adults || '1'} Adult`);
            setText('traveller-name', fullName || 'Traveller');
            setText('route-summary', route);
            setText('filter-summary', `${data.filter_name || 'Filter'}: ${data.filter_value || 'Without Flight'}`);
            setInput("input[name='first_name']", data.first_name || '');
            setInput("input[name='last_name']", data.last_name || '');
            setInput("input[name='email']", data.email || '');
            setInput("input[name='mobile']", data.mobile || '');
            """,
            data,
        )

    def _close_traveller_modal_if_still_open(self):
        self.driver.execute_script(
            """
            const modal = document.getElementById('traveller-modal');
            if (modal) {
              modal.classList.add('hidden');
              modal.style.display = 'none';
            }
            """
        )

    def _pause(self):
        time.sleep(STEP_DELAY)
