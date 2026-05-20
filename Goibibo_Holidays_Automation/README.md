# Goibibo Holidays Automation

Selenium Python PyTest framework using Page Object Model.

## Flow

Goibibo homepage -> Holidays -> search package data from CSV/Excel -> 1 room, 1 guest -> package listing -> checkout/payment boundary -> traveller details -> contact/GST review -> payment method -> enter dummy card details -> stop.

## Run

```bash
pip install -r requirements.txt
pytest tests/test_holidays.py -s
```

Run the 4 positive and 2 negative cases:

```bash
pytest tests/test_positive_negative.py -s
```

Run all scenarios:

```bash
pytest -s
```

Run the main test and open both reports:

```bash
run_e2e_with_reports.bat
```

Run all tests and open both reports:

```bash
run_all_tests_with_reports.bat
```

## Output

- Screenshots: `screenshots/`
- Logs: `logs/`
- HTML report: `reports/goibibo_holidays_report.html`
- Allure result files: `reports/allure-results`
- Allure report: `reports/allure-report/index.html`
- CSV test data: `testdata/holiday_test_data.csv`
- Excel test data: `testdata/holiday_test_data.xlsx`

Allure is installed locally in the project. To generate it manually:

```bash
node_modules\.bin\allure.cmd generate reports\allure-results --clean -o reports\allure-report
```

After a normal pytest execution, the project also tries to generate and open Allure automatically.

Positive cases:

- `TC_POS_001`: Hyderabad to Goa, traveller Deekshith Vanaparthi
- `TC_POS_002`: Mumbai to Rajasthan, traveller Rahul Sharma
- `TC_POS_003`: Bengaluru to Kerala, traveller Priya Reddy
- `TC_POS_004`: Chennai to Andaman, traveller Ananya Rao

Negative cases:

- `TC_NEG_001`: empty first name
- `TC_NEG_002`: invalid mobile number

The final Pay button is never clicked.
