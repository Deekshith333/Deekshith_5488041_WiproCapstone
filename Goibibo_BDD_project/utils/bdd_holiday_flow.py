import json

import allure

from pages.homepage import HomePage
from pages.packages_page import PackagesPage
from pages.payment_page import PaymentPage
from pages.search_page import SearchPage
from utils.data_reader import get_case


def run_holiday_booking_flow(context, case_id):
    context.case_id = case_id
    context.data = get_case(case_id)
    allure.dynamic.title(f"{case_id} - {context.data['case_name']}")
    allure.dynamic.description(context.data["case_description"])
    allure.attach(
        json.dumps(context.data, indent=2),
        name=f"test_data_{case_id}",
        attachment_type=allure.attachment_type.JSON,
    )

    home = HomePage(context.driver)
    search = SearchPage(context.driver)
    packages = PackagesPage(context.driver)
    payment = PaymentPage(context.driver)

    with allure.step("Launch Goibibo homepage"):
        home.launch_website()
    with allure.step("Navigate from homepage to Goibibo Holidays module"):
        home.navigate_to_holidays()
    with allure.step("Enter search details from test data"):
        search.enter_search_details(context.data)
    with allure.step("Wait for package listing and apply scenario filter"):
        packages.wait_for_package_listing()
        packages.apply_requested_filter(context.data)
    with allure.step("Open checkout/payment boundary page"):
        packages.open_checkout_directly()
    with allure.step("Fill traveller, contact and GST details"):
        payment.enter_traveller_details(context.data)

    if context.data["case_type"] == "negative":
        context.validation_message = payment.get_validation_message(context.data)
        return

    with allure.step("Select credit/debit card and enter dummy card details"):
        payment.select_card_and_enter_details(context.data)
