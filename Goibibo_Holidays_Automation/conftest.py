from datetime import datetime
import os
import subprocess

import pytest

from config import REPORT_DIR, ROOT_DIR, SCREENSHOT_DIR
from utils.driver_setup import create_driver
from utils.logger import get_logger

logger = get_logger("pytest")


@pytest.fixture
def driver():
    driver_instance = create_driver()
    logger.info("Started Chrome browser")
    yield driver_instance
    logger.info("Closing Chrome browser")
    try:
        driver_instance.quit()
    except Exception:
        logger.warning("Chrome browser was already closed")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        driver_instance = item.funcargs.get("driver")
        if driver_instance:
            SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
            screenshot = SCREENSHOT_DIR / f"{item.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            try:
                driver_instance.save_screenshot(str(screenshot))
                logger.error("Failure screenshot saved: %s", screenshot)
            except Exception as exc:
                logger.error("Could not save failure screenshot because browser session was closed: %s", exc)


def pytest_sessionfinish(session, exitstatus):
    if session.config.option.collectonly:
        return

    allure_cmd = ROOT_DIR / "node_modules" / ".bin" / "allure.cmd"
    allure_results = REPORT_DIR / "allure-results"
    allure_report = REPORT_DIR / "allure-report"

    if not allure_results.exists():
        logger.warning("Allure result folder not found. Skipping Allure report generation.")
        return

    try:
        command = [str(allure_cmd)] if allure_cmd.exists() else ["npx.cmd", "allure"]
        subprocess.run(
            command + ["generate", str(allure_results), "--clean", "-o", str(allure_report)],
            cwd=str(ROOT_DIR),
            check=True,
            timeout=90,
        )
        index_file = allure_report / "index.html"
        if index_file.exists():
            os.startfile(str(index_file))
            logger.info("Allure report opened: %s", index_file)
    except Exception as exc:
        logger.error("Could not generate/open Allure report automatically: %s", exc)
