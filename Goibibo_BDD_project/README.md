# Goibibo Holidays BDD Automation

BDD Selenium Python framework for Goibibo Holidays using Behave, Page Object Model, screenshots, logs, JSON/JUnit reports and Allure reports.

## Test Coverage

- 1 end-to-end scenario
- 5 positive scenarios
- 2 negative scenarios
- Total: 8 BDD scenarios

## BDD Structure

- End-to-end feature: `features/end_to_end.feature`
- End-to-end steps: `features/steps/end_to_end_steps.py`
- Positive and negative feature: `features/positive_negative.feature`
- Positive and negative steps: `features/steps/positive_negative_steps.py`
- Shared reusable business flow: `utils/bdd_holiday_flow.py`

## Main Run Command

```bash
run_bdd_with_reports.bat
```

This runs all BDD scenarios and opens the Allure report.

## Separate Run Commands

```bash
run_e2e_only.bat
run_positive_negative_only.bat
```

Or run directly:

```bash
.venv\Scripts\python.exe -m behave features\end_to_end.feature
.venv\Scripts\python.exe -m behave features\positive_negative.feature
```

## Manual Commands

```bash
.venv\Scripts\python.exe -m behave
node_modules\.bin\allure.cmd generate reports\allure-results --clean -o reports\allure-report
node_modules\.bin\allure.cmd open reports\allure-report
```

## Reports

- Allure results: `reports/allure-results`
- Allure report: `reports/allure-report/index.html`
- Behave JSON report: `reports/behave_report.json`
- JUnit XML report: `reports/junit`
- Console report: `reports/console_report.txt`
- Screenshots: `screenshots`
- Logs: `logs`

## Safety

The automation only enters dummy card details and stops. It never clicks the final Pay button.
