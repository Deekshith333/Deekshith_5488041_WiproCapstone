import allure
import json

from pages.homepage import HomePage
from pages.searchpage import SearchPage
from pages.packagespage import PackagesPage
from pages.paymentpage import PaymentPage
from utils.data_reader import get_case


@allure.title("Goibibo Holidays end-to-end booking until card details boundary")
@allure.description("Searches a holiday package, fills traveller/review details, proceeds to payment, enters dummy card data, and stops before Pay.")
def test_goibibo_holidays_end_to_end_until_card_boundary(driver):
    data = get_case("TC_POS_001")
    allure.attach(
        json.dumps(data, indent=2),
        name="test_data_TC_POS_001",
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

    with allure.step("Enter holiday search details"):
        search.enter_search_details(data)

    with allure.step("Wait for package listing page"):
        packages.wait_for_package_listing()
    with allure.step("Open checkout/payment boundary"):
        packages.open_checkout_directly()

    with allure.step("Enter traveller, contact and GST details"):
        payment.enter_traveller_details(data)

    with allure.step("Select credit/debit card and enter dummy card details"):
        payment.select_card_and_enter_details()
    with allure.step("Verify card details boundary is reached"):
        assert payment.page_contains("card", timeout=5) or payment.page_contains("CVV", timeout=5)
