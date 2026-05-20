import allure
import pytest

from pages.homepage import HomePage
from pages.packagespage import PackagesPage
from pages.paymentpage import PaymentPage
from pages.searchpage import SearchPage
from utils.data_reader import get_case


TEST_CASES = [
    pytest.param("TC_POS_001", id="positive-route-hyderabad-to-goa", marks=pytest.mark.positive),
    pytest.param("TC_POS_002", id="positive-route-mumbai-to-rajasthan", marks=pytest.mark.positive),
    pytest.param("TC_POS_003", id="positive-route-bengaluru-to-kerala", marks=pytest.mark.positive),
    pytest.param("TC_POS_004", id="positive-route-chennai-to-andaman", marks=pytest.mark.positive),
    pytest.param("TC_NEG_001", id="negative-empty-first-name", marks=pytest.mark.negative),
    pytest.param("TC_NEG_002", id="negative-invalid-phone", marks=pytest.mark.negative),
]


@pytest.mark.parametrize("case_id", TEST_CASES)
@allure.title("Goibibo Holidays positive and negative data-driven case")
@allure.description("Runs data-driven positive and negative scenarios from the CSV/XLSX test data.")
def test_positive_and_negative_holiday_cases(case_id, driver):
    data = get_case(case_id)
    home = HomePage(driver)
    search = SearchPage(driver)
    packages = PackagesPage(driver)
    payment = PaymentPage(driver)

    home.launch_website()
    home.navigate_to_holidays()
    search.enter_search_details(data)
    packages.wait_for_package_listing()
    packages.open_checkout_directly()
    payment.enter_traveller_details(data)

    if data["case_type"] == "negative":
        payment.verify_negative_validation_or_boundary(data["expected_error"])
        return

    payment.select_card_and_enter_details()
    assert payment.page_contains("card", timeout=5) or payment.page_contains("CVV", timeout=5)
