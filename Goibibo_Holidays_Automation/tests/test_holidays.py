import allure

from pages.homepage import HomePage
from pages.searchpage import SearchPage
from pages.packagespage import PackagesPage
from pages.paymentpage import PaymentPage
from utils.data_reader import get_case


@allure.title("Goibibo Holidays end-to-end booking until card details boundary")
@allure.description("Searches a holiday package, fills traveller/review details, proceeds to payment, enters dummy card data, and stops before Pay.")
def test_goibibo_holidays_end_to_end_until_card_boundary(driver):
    data = get_case("TC_POS_001")
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

    payment.select_card_and_enter_details()
    assert payment.page_contains("card", timeout=5) or payment.page_contains("CVV", timeout=5)
