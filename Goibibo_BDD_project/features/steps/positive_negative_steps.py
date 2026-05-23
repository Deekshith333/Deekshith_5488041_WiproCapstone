import allure
from behave import then, when

from pages.payment_page import PaymentPage
from utils.bdd_holiday_flow import run_holiday_booking_flow


@when('I execute the positive or negative Goibibo Holidays journey for case "{case_id}"')
def step_execute_positive_negative_journey(context, case_id):
    run_holiday_booking_flow(context, case_id)


@then("the positive journey should stop at card details boundary")
def step_positive_boundary(context):
    payment = PaymentPage(context.driver)
    assert context.data["case_type"] == "positive"
    assert payment.card_boundary_reached(), "Card details boundary was not reached."


@then("the negative validation should be reported")
def step_negative_validation(context):
    assert context.data["case_type"] == "negative"
    assert context.validation_message, "Negative validation message was not captured."
    allure.attach(
        context.validation_message,
        name=f"{context.case_id}_negative_validation",
        attachment_type=allure.attachment_type.TEXT,
    )
