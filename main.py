import os
import re
import json
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import pandas as pd
from urllib.parse import urljoin

# --- Load environment variables ---
load_dotenv()
WEBSITE_URL = os.getenv("WEBSITE_URL") or "https://app.littlehotelier.com/"
USER_EMAIL = os.getenv("USER_EMAIL")
USER_PASS = os.getenv("USER_PASS")


# --- Helper Functions ---
def wait_for(driver, locator, timeout=15):
    """Wait until the element is present and return it."""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))


def get_date_input(label):
    """Ask for date input, validate format & value, convert to 'DD MON YYYY'."""
    date_pattern = re.compile(r"^\d{2}-\d{2}-\d{4}$")

    while True:
        user_input = input(f"Enter {label} date (DD-MM-YYYY): ").strip()

        # Step 1: Check format first
        if not date_pattern.match(user_input):
            print("❌ Wrong format. Please use DD-MM-YYYY (e.g. 22-10-2025).")
            continue

        # Step 2: Check if the date is real
        try:
            parsed_date = datetime.strptime(user_input, "%d-%m-%Y")
            formatted_date = parsed_date.strftime("%d %b %Y").upper()
            return [user_input, formatted_date]
        except ValueError:
            print(
                "❌ Invalid date. That date does not exist on the calendar (e.g. 30-02-2025 is invalid)."
            )


# --- Core Functional Blocks ---
def initialize_driver():
    """Initialize and return a Chrome WebDriver instance."""
    print("Initializing Chrome WebDriver...")
    driver = webdriver.Chrome()
    driver.maximize_window()
    return driver


def login(driver):
    """Perform login using credentials from the .env file."""
    print("Navigating to website...")
    driver.get(WEBSITE_URL)

    # --- Wait for email field ---
    EMAIL_FIELD_SELECTOR = (By.NAME, "username")
    email_field = wait_for(driver, EMAIL_FIELD_SELECTOR)
    print(f"Entering email: {USER_EMAIL}")
    email_field.send_keys(USER_EMAIL, Keys.ENTER)

    # --- Wait for password field ---
    PASSWORD_FIELD_SELECTOR = (By.NAME, "password")
    password_field = wait_for(driver, PASSWORD_FIELD_SELECTOR)
    print("Entering password...")
    password_field.send_keys(USER_PASS, Keys.ENTER)

    # --- Wait for dashboard to load ---
    print("Waiting for dashboard to load...")
    DASHBOARD_READY_SELECTOR = (By.ID, "horizontal-nav-item-reservations")
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located(DASHBOARD_READY_SELECTOR)
    )

    print("Login successful!")


def apply_date_filters(driver, date_from, date_to):
    """
    Clears existing text in the date filter inputs and applies new date range.
    """
    DATE_FROM_SELECTOR = (By.NAME, "reservation_filter[date_from_display]")
    DATE_TO_SELECTOR = (By.NAME, "reservation_filter[date_to_display]")

    print(f"🗓 Applying date filters: {date_from} → {date_to}")

    # --- Store the current URL ---
    old_url = driver.current_url

    # --- Fill in the filters ---
    date_from_field = wait_for(driver, DATE_FROM_SELECTOR)
    date_from_field.clear()
    date_from_field.send_keys(date_from)

    date_to_field = wait_for(driver, DATE_TO_SELECTOR)
    date_to_field.clear()
    date_to_field.send_keys(date_to)
    
    # --- Submit the form ---
    driver.find_element(By.XPATH, "//button[@type='submit']").click()

    # --- Wait for URL to update ---
    print("⏳ Waiting for URL to update after applying filters...")
    WebDriverWait(driver, 30).until(lambda d: d.current_url != old_url)

def download_and_parse_csv(driver, date_from, date_to):
    """Download reservations CSV and convert to JSON."""
    print("📥 Getting CSV export link...")

    # 1. Find the export link
    export_link = wait_for(driver, (By.CSS_SELECTOR, "a.export"))
    href = export_link.get_attribute("href")
    full_url = urljoin(driver.current_url, href)

    # 2. Extract cookies from Selenium
    selenium_cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in selenium_cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    # 3. Download CSV
    print(f"⬇️ Downloading CSV from: {full_url}")
    response = session.get(full_url)
    response.raise_for_status()

    # 4. Read CSV into pandas
    df = pd.read_csv(StringIO(response.text)) if hasattr(pd, 'compat') else pd.read_csv(StringIO(response.text))

    # 5. Clean & select columns
    columns_to_keep = [
        "Status",
        "Guest first name",
        "Guest last name",
        "Booking reference",
        "Source",
        "Occupants",
        "Check in date",
        "Check out date",
        "Booked",
        "ETA",
        "Rooms",
        "Payment total",
        "Payment outstanding",
        "Invoice Number",
        "Guest email",
        "Guest phone number",
    ]
 
    df = df.where(pd.notnull(df), None).convert_dtypes()
    df = df[[col for col in columns_to_keep if col in df.columns]]

    # 6. Convert to JSON
    reservations_json = df.to_dict(orient="records")
    print(f"✅ {len(reservations_json)} reservations found.")

    # 7. Save JSON to file
    print("💾 Saving reservations to file...")
    output_filename = f"reservations_{date_from}_to_{date_to}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(reservations_json, f, ensure_ascii=False, indent=2)

    print(f"💾 Saved reservations to {os.path.abspath(output_filename)}")

    return reservations_json

def run_scraper():
    """Main scraper entrypoint that orchestrates all steps."""
    # Ask for date filters
    date_from = get_date_input("start")
    date_to = get_date_input("end")

    if not all([WEBSITE_URL, USER_EMAIL, USER_PASS]):
        print("ERROR: Missing environment variables.")
        return

    driver = None
    try:
        driver = initialize_driver()
        login(driver)

        # --- TODO: Add reservation scraping logic here ---
        # Example structure:
        # click_reservations_tab(driver)
        driver.find_element(By.LINK_TEXT, "Reservations").click()
        # apply_date_filters(driver)
        apply_date_filters(driver, date_from[1], date_to[1])
        download_and_parse_csv(driver, date_from[0], date_to[0])

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if driver:
            driver.quit()
            print("Browser closed.")


# --- Run ---
if __name__ == "__main__":
    run_scraper()
