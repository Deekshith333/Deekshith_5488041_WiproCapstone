import allure
import json
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
    pytest.param("TC_POS_005", id="positive-route-cochin-to-thailand", marks=pytest.mark.positive),
    pytest.param("TC_NEG_001", id="negative-empty-first-name", marks=pytest.mark.negative),
    pytest.param("TC_NEG_002", id="negative-invalid-phone", marks=pytest.mark.negative),
]


@pytest.mark.parametrize("case_id", TEST_CASES)
@allure.title("Goibibo Holidays positive and negative data-driven case")
@allure.description("Runs data-driven positive and negative scenarios from the CSV/XLSX test data.")
def test_positive_and_negative_holiday_cases(case_id, driver):
    data = get_case(case_id)
    allure.dynamic.title(f"{case_id} - {data['case_type']} Goibibo Holidays scenario")
    allure.attach(
        json.dumps(data, indent=2),
        name=f"test_data_{case_id}",
        attachment_type=allure.attachment_type.JSON,
    )
    home = HomePage(driver)
    search = SearchPage(driver)
    packages = PackagesPage(driver)
    payment = PaymentPage(driver)

    with allure.step("Launch Goibibo website"):
        home.launch_website()
    with allure.step("Navigate to Holidays module"):
        home.navigate_to_holidays()
    with allure.step("Enter holiday search details from test data"):
        search.enter_search_details(data)
    with allure.step("Wait for package listing page"):
        packages.wait_for_package_listing()
    with allure.step("Open checkout/payment boundary"):
        packages.open_checkout_directly()
    with allure.step("Enter traveller, contact and GST details"):
        payment.enter_traveller_details(data)

    if data["case_type"] == "negative":
        with allure.step("Verify negative validation or boundary behavior"):
            payment.verify_negative_validation_or_boundary(data["expected_error"])
        return

    with allure.step("Select credit/debit card and enter dummy card details"):
        payment.select_card_and_enter_details()
    with allure.step("Verify card details boundary is reached"):
        assert payment.page_contains("card", timeout=5) or payment.page_contains("CVV", timeout=5)
