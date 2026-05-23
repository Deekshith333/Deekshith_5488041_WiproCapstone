from pathlib import Path

import allure

from config import LOG_DIR, REPORT_DIR, SCREENSHOT_DIR
from utils.driver_setup import create_driver
from utils.logger import get_logger


def before_all(context):
    for folder in [LOG_DIR, REPORT_DIR, SCREENSHOT_DIR]:
        folder.mkdir(parents=True, exist_ok=True)
    context.logger = get_logger("behave")


def before_scenario(context, scenario):
    context.driver = create_driver()
    context.logger.info("Started Chrome for scenario: %s", scenario.name)
    context.scenario_status_message = ""


def after_step(context, step):
    if step.status == "failed" and hasattr(context, "driver"):
        path = SCREENSHOT_DIR / f"failed_{_safe_name(context.scenario.name)}_{_safe_name(step.name)}.png"
        try:
            context.driver.save_screenshot(str(path))
            allure.attach.file(str(path), name="failed_step_screenshot", attachment_type=allure.attachment_type.PNG)
        except Exception as exc:
            context.logger.error("Could not capture failed step screenshot: %s", exc)


def after_scenario(context, scenario):
    log_file = getattr(context.logger, "log_file_path", None)
    if log_file and Path(log_file).exists():
        try:
            allure.attach.file(log_file, name="execution_log", attachment_type=allure.attachment_type.TEXT)
        except Exception:
            pass

    if hasattr(context, "driver"):
        context.logger.info("Closing Chrome for scenario: %s", scenario.name)
        try:
            context.driver.quit()
        except Exception:
            context.logger.warning("Chrome was already closed")


def _safe_name(value):
    return "".join(ch if ch.isalnum() else "_" for ch in value)[:120]
