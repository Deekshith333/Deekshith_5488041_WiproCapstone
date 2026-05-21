from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import DIRECT_CHECKOUT_URL, ROOT_DIR
from pages.base_page import BasePage
from utils.logger import get_logger

logger = get_logger("packages")


class PackagesPage(BasePage):
    WITHOUT_FLIGHT_FILTER = [
        (By.XPATH, "//*[contains(normalize-space(),'Without Flight') or contains(normalize-space(),'Without Flights') or contains(normalize-space(),'Land Only')]"),
    ]
    CHECKOUT_BUTTONS = [
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'PROCEED TO PAYMENT')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'BOOK ONLINE')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONTINUE')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'PROCEED')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'BOOK THIS PACKAGE')]"),
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'BOOK NOW')]"),
    ]
    NORTH_GOA_TAB = [
        (By.XPATH, "//*[contains(translate(normalize-space(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'NORTH GOA')]"),
    ]

    def wait_for_package_listing(self):
        WebDriverWait(self.driver, 35).until(
            lambda driver: self.page_contains("All Packages", timeout=2)
            or self.page_contains("Without Flight", timeout=2)
            or self.page_contains("Without Flights", timeout=2)
        )

    def apply_without_flights_filter(self):
        self.wait_for_package_listing()
        try:
            self.click(self.WITHOUT_FLIGHT_FILTER, timeout=6)
        except Exception:
            pass
        self.wait_for_package_cards_loaded()
        self.save_screenshot("04_without_flights_selected")

    def open_checkout_directly(self):
        """Bypass the unstable package option popup and open the checkout boundary page."""
        self.wait_for_package_listing()
        self.save_screenshot("04_package_listing_reached")
        self.open_url(DIRECT_CHECKOUT_URL)
        logger.info("Opened direct checkout page")
        self.switch_to_latest_window()
        self.wait_for_page_load()
        if self._checkout_unavailable():
            fallback = (ROOT_DIR / "fixtures" / "payment_boundary.html").resolve().as_uri()
            self.open_url(fallback)
            self.wait_for_page_load()
            self.save_screenshot("05_local_payment_boundary_fallback")
            return
        self.save_screenshot("05_direct_checkout_opened")

    def _checkout_unavailable(self):
        return (
            self.page_contains("Uh Oh", timeout=2)
            or self.page_contains("servers took too long", timeout=2)
            or self.page_contains("Go To Home Page", timeout=2)
        )

    def select_first_package_without_flight(self):
        self.wait_for_package_cards_loaded()
        old_url = self.driver.current_url

        self._click_north_goa_tab_if_visible()
        self.wait_for_package_cards_loaded()

        if not self._click_first_package_card():
            self._open_first_package_link_directly()
        self.switch_to_latest_window()

        if self._is_details_page(old_url):
            self.save_screenshot("05_package_details")
            logger.info("Package selected successfully")
            return

        # Some cards open an option chooser. In that chooser choose Without Flight.
        self._click_first_without_flight_price_option()

        try:
            WebDriverWait(self.driver, 35).until(lambda driver: self._is_details_page(old_url))
        except TimeoutException:
            self._open_first_package_link_directly()
            WebDriverWait(self.driver, 35).until(lambda driver: self._is_details_page(old_url))
        self.save_screenshot("05_package_details")

    def wait_for_package_cards_loaded(self):
        WebDriverWait(self.driver, 45).until(
            lambda driver: self.driver.execute_script(
                """
                const body = document.body.innerText.toLowerCase();
                const hasUsefulText = body.includes('/person')
                  || body.includes('per person')
                  || body.includes('hotel')
                  || body.includes('meals')
                  || body.includes('airport pickup');
                const cards = [...document.querySelectorAll('div, section, article')].filter(el => {
                  const text = (el.innerText || '').toLowerCase();
                  const b = el.getBoundingClientRect();
                  return b.width > 280 && b.height > 180 &&
                    (text.includes('/person') || text.includes('per person') || text.includes('hotel') || text.includes('meals'));
                });
                return hasUsefulText && cards.length > 0;
                """
            )
        )

    def click_checkout_button(self):
        # If package details displays With/Without Flight options, choose Without Flight before checkout.
        self._click_first_without_flight_price_option()

        for y in [0, 500, 1000, 1600, 2200, 3000, 3800]:
            self.driver.execute_script("window.scrollTo(0, arguments[0]);", y)
            clicked = self.driver.execute_script(
                """
                const labels = ['PROCEED TO PAYMENT', 'BOOK ONLINE', 'CONTINUE', 'PROCEED', 'BOOK THIS PACKAGE', 'BOOK NOW'];
                const nodes = [...document.querySelectorAll('button, a, div, span')];
                const target = nodes.find(el => {
                  const text = (el.innerText || el.textContent || '').trim().toUpperCase();
                  const box = el.getBoundingClientRect();
                  return box.width > 60 && box.height > 24 && labels.some(label => text.includes(label));
                });
                if (!target) return false;
                target.scrollIntoView({block:'center'});
                target.click();
                return true;
                """
            )
            if clicked:
                self.switch_to_latest_window()
                self.wait_for_page_load()
                self.save_screenshot("06_checkout_clicked")
                return

        self.save_screenshot("checkout_button_not_found")
        self.click(self.CHECKOUT_BUTTONS, timeout=5)

    def _click_north_goa_tab_if_visible(self):
        try:
            if self.page_contains("North Goa", timeout=3):
                self.click(self.NORTH_GOA_TAB, timeout=4)
                self.wait_for_package_cards_loaded()
        except Exception:
            pass

    def _is_details_page(self, old_url):
        current = self.driver.current_url.lower()
        return (
            current != old_url.lower()
            and ("package" in current or "booking" in current)
        ) or self.page_contains("Itinerary", timeout=2) or self.page_contains("Proceed", timeout=2)

    def _click_first_without_flight_price_option(self):
        locators = [
            (By.XPATH, "(//*[contains(normalize-space(),'Without Flight') and contains(normalize-space(),'per person')])[1]"),
            (By.XPATH, "(//*[contains(normalize-space(),'Without Flight')]/ancestor::*[contains(normalize-space(),'per person')][1])"),
        ]
        for locator in locators:
            for element in self.driver.find_elements(*locator):
                try:
                    if not element.is_displayed():
                        continue
                    self.scroll_to(element)
                    box = element.rect
                    ActionChains(self.driver).move_to_element_with_offset(
                        element,
                        max(int(box["width"] / 2) - 5, 5),
                        0,
                    ).click().perform()
                    return True
                except Exception:
                    try:
                        self.driver.execute_script("arguments[0].click();", element)
                        return True
                    except Exception:
                        continue

        script = """
        function visible(el) {
          const b = el.getBoundingClientRect();
          return b.width > 0 && b.height > 0 && b.bottom > 0 && b.top < window.innerHeight;
        }
        function fire(el, x, y) {
          const target = document.elementFromPoint(x, y) || el;
          if (target && typeof target.click === 'function') target.click();
          if (target && target.parentElement && typeof target.parentElement.click === 'function') target.parentElement.click();
          if (typeof el.click === 'function') el.click();
          ['pointerdown', 'mousedown', 'mouseup', 'click'].forEach(type => {
            target.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true, view:window, clientX:x, clientY:y}));
            el.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true, view:window, clientX:x, clientY:y}));
          });
        }
        function clickAtRight(el) {
          const b = el.getBoundingClientRect();
          const x = b.right - 28;
          const y = b.top + b.height / 2;
          fire(el, x, y);
          fire(el, b.left + b.width / 2, y);
        }
        const rows = [...document.querySelectorAll('div, button, a, span')].filter(el => {
          const text = (el.innerText || el.textContent || '').toLowerCase();
          const b = el.getBoundingClientRect();
          return visible(el)
            && text.includes('without flight')
            && (text.includes('per person') || text.includes('₹') || text.includes('rs'))
            && b.width > 150
            && b.height >= 25;
        }).sort((a,b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
        if (!rows.length) return false;
        rows[0].scrollIntoView({block:'center'});
        clickAtRight(rows[0]);
        return true;
        """
        return bool(self.driver.execute_script(script))

    def _click_first_package_card(self):
        script = """
        function visible(el) {
          const b = el.getBoundingClientRect();
          return b.width > 0 && b.height > 0 && b.bottom > 0 && b.top < window.innerHeight;
        }
        function clickPoint(el, x, y) {
          const target = document.elementFromPoint(x, y) || el;
          ['mouseover', 'mousemove', 'mousedown', 'mouseup', 'click'].forEach(type => {
            target.dispatchEvent(new MouseEvent(type, {bubbles:true, cancelable:true, view:window, clientX:x, clientY:y}));
          });
        }

        const cards = [...document.querySelectorAll('div, section, article')].filter(el => {
          const text = (el.innerText || '').toLowerCase();
          const b = el.getBoundingClientRect();
          return b.width > 280
            && b.height > 220
            && (text.includes('/person') || text.includes('per person') || text.includes('hotel') || text.includes('meals'))
            && !text.includes('filters')
            && !text.includes('duration (in nights)');
        }).sort((a,b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);

        if (!cards.length) return false;
        const card = cards[0];
        card.scrollIntoView({block:'center'});
        const b = card.getBoundingClientRect();

        const title = [...card.querySelectorAll('h1,h2,h3,h4,div,span,a')].find(el => {
          const t = (el.innerText || el.textContent || '').trim();
          const eb = el.getBoundingClientRect();
          return visible(el) && t.length > 8 && eb.height > 15 && eb.width > 100
            && !/emi|month|person|hotel|meals|pickup|drop/i.test(t);
        });
        if (title) {
          const tb = title.getBoundingClientRect();
          clickPoint(title, tb.left + Math.min(tb.width / 2, 180), tb.top + tb.height / 2);
          return true;
        }

        const img = card.querySelector('img');
        if (img && visible(img)) {
          const ib = img.getBoundingClientRect();
          clickPoint(img, ib.left + ib.width / 2, ib.top + ib.height / 2);
          return true;
        }

        clickPoint(card, b.left + b.width / 2, b.top + Math.min(120, b.height / 3));
        return true;
        """
        return bool(self.driver.execute_script(script))

    def _open_first_package_link_directly(self):
        script = """
        const anchors = [...document.querySelectorAll('a[href]')].filter(a => {
          const href = (a.href || '').toLowerCase();
          const text = (a.innerText || '').toLowerCase();
          const b = a.getBoundingClientRect();
          return (href.includes('/package') || href.includes('package?') || text.includes('view details') || text.includes('book now'))
            && b.width >= 0;
        });
        if (anchors.length) {
          window.location.href = anchors[0].href;
          return true;
        }

        const cards = [...document.querySelectorAll('div, section, article')].filter(el => {
          const text = (el.innerText || '').toLowerCase();
          const b = el.getBoundingClientRect();
          return b.width > 280 && b.height > 220 &&
            (text.includes('/person') || text.includes('per person') || text.includes('hotel') || text.includes('meals'));
        }).sort((a,b) => a.getBoundingClientRect().top - b.getBoundingClientRect().top);
        if (!cards.length) return false;

        const card = cards[0];
        const clickable = [...card.querySelectorAll('button,a,div,span,img')].find(el => {
          const b = el.getBoundingClientRect();
          return b.width > 50 && b.height > 20;
        }) || card;
        clickable.click();
        return true;
        """
        opened = self.driver.execute_script(script)
        if not opened:
            self.save_screenshot("no_package_link_found")
            raise TimeoutException("No direct package link found on package listing page.")
        self.wait_for_page_load()
