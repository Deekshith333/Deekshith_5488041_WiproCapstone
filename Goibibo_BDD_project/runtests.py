import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
REPORT_DIR = ROOT_DIR / "reports"
ALLURE_RESULTS_DIR = REPORT_DIR / "allure-results"
ALLURE_REPORT_DIR = REPORT_DIR / "allure-report"
JUNIT_DIR = REPORT_DIR / "junit"
LOG_DIR = ROOT_DIR / "logs"
SCREENSHOT_DIR = ROOT_DIR / "screenshots"
PACKAGE_JSON = ROOT_DIR / "package.json"
LOCAL_ALLURE = ROOT_DIR / "node_modules" / ".bin" / "allure.cmd"


def run_command(command, description, check=True):
    print(f"\n=== {description} ===")
    print(" ".join(f'"{part}"' if " " in str(part) else str(part) for part in command))
    completed = subprocess.run(command, cwd=ROOT_DIR, text=True)
    if check and completed.returncode != 0:
        raise SystemExit(completed.returncode)
    return completed.returncode


def ensure_folders():
    for folder in [REPORT_DIR, ALLURE_RESULTS_DIR, JUNIT_DIR, LOG_DIR, SCREENSHOT_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def clean_report_folders():
    for folder in [ALLURE_RESULTS_DIR, ALLURE_REPORT_DIR]:
        if folder.exists():
            shutil.rmtree(folder)
    ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    JUNIT_DIR.mkdir(parents=True, exist_ok=True)


def ensure_package_json():
    if PACKAGE_JSON.exists():
        return
    PACKAGE_JSON.write_text(
        json.dumps({"devDependencies": {"allure-commandline": "^2.41.0"}}, indent=2),
        encoding="utf-8",
    )


def ensure_local_allure(skip_install=False):
    if LOCAL_ALLURE.exists():
        return
    if skip_install:
        raise SystemExit(
            "Local Allure CLI was not found. Run: npm.cmd install --save-dev allure-commandline"
        )
    ensure_package_json()
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise SystemExit(
            "npm is not available, so the local Allure CLI cannot be installed automatically."
        )
    run_command([npm, "install"], "Installing local Allure command line")
    if not LOCAL_ALLURE.exists():
        raise SystemExit("Allure installation finished, but node_modules/.bin/allure.cmd was not found.")


def build_behave_command(args):
    command = [
        sys.executable,
        "-m",
        "behave",
        "-f",
        "pretty",
        "-o",
        str(REPORT_DIR / "console_report.txt"),
        "-f",
        "allure_behave.formatter:AllureFormatter",
        "-o",
        str(ALLURE_RESULTS_DIR),
        "-f",
        "json.pretty",
        "-o",
        str(REPORT_DIR / "behave_report.json"),
        "--junit",
        "--junit-directory",
        str(JUNIT_DIR),
    ]
    if args.tags:
        command.extend(["--tags", args.tags])
    if args.feature:
        command.append(args.feature)
    return command


def generate_allure_report():
    run_command(
        [
            str(LOCAL_ALLURE),
            "generate",
            str(ALLURE_RESULTS_DIR),
            "--clean",
            "-o",
            str(ALLURE_REPORT_DIR),
        ],
        "Generating Allure HTML report",
    )


def open_allure_report():
    print("\n=== Opening Allure report ===")
    subprocess.Popen(
        [str(LOCAL_ALLURE), "open", str(ALLURE_REPORT_DIR)],
        cwd=ROOT_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform.startswith("win") else 0,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run Goibibo Holidays BDD automation and open Allure report automatically."
    )
    parser.add_argument(
        "--feature",
        help="Optional feature file path. Example: features/end_to_end.feature",
    )
    parser.add_argument(
        "--tags",
        help="Optional Behave tag expression. Example: @e2e or @positive",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Generate Allure report but do not open it.",
    )
    parser.add_argument(
        "--skip-allure-install",
        action="store_true",
        help="Do not auto-install local Allure CLI if missing.",
    )
    parser.add_argument(
        "--keep-old-results",
        action="store_true",
        help="Do not delete old allure-results/allure-report before running.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    ensure_folders()
    if not args.keep_old_results:
        clean_report_folders()
    ensure_local_allure(skip_install=args.skip_allure_install)

    behave_exit_code = run_command(
        build_behave_command(args),
        "Running Goibibo Holidays BDD automation",
        check=False,
    )

    if any(ALLURE_RESULTS_DIR.iterdir()):
        generate_allure_report()
        if not args.no_open:
            open_allure_report()
    else:
        print("No Allure result files were generated, so the Allure report was not opened.")

    if behave_exit_code == 0:
        print("\nAutomation completed successfully.")
    else:
        print(f"\nAutomation completed with failures. Behave exit code: {behave_exit_code}")
    raise SystemExit(behave_exit_code)


if __name__ == "__main__":
    main()
