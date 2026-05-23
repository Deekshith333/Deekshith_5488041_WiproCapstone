from behave import then, when

from pages.payment_page import PaymentPage
from utils.bdd_holiday_flow import run_holiday_booking_flow


@when('I execute the complete end to end Goibibo Holidays journey for case "{case_id}"')
def step_execute_end_to_end_journey(context, case_id):
    run_holiday_booking_flow(context, case_id)


@then("the end to end journey should stop at card details boundary")
def step_end_to_end_boundary(context):
    payment = PaymentPage(context.driver)
    assert context.data["case_type"] == "e2e"
    assert payment.card_boundary_reached(), "Card details boundary was not reached."
