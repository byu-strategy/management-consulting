#!/usr/bin/env python3
"""
Simple test script to debug LinkedIn automation.
Uses a fresh profile to avoid Chrome profile locking issues.
"""

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


SCRIPT_DIR = Path(__file__).parent
PROFILE_DIR = SCRIPT_DIR / ".chrome_profile"


def main():
    print("=" * 60)
    print("LinkedIn Company ID Lookup - Test Script")
    print("=" * 60)

    options = Options()

    # Use a dedicated profile directory for this script
    # (avoids conflicts with your main Chrome)
    PROFILE_DIR.mkdir(exist_ok=True)
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    # Disable automation detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    print("\n1. Installing/finding ChromeDriver...")
    service = Service(ChromeDriverManager().install())

    print("2. Launching Chrome...")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    try:
        url = "https://www.linkedin.com/school/brigham-young-university/people/"
        print(f"3. Navigating to: {url}")
        driver.get(url)

        print("4. Waiting 5 seconds for page to load...")
        time.sleep(5)

        print(f"\n   Current URL: {driver.current_url}")
        print(f"   Page title: {driver.title}")

        # Check if we're logged in or need to log in
        if "login" in driver.current_url.lower() or "signin" in driver.current_url.lower() or "checkpoint" in driver.current_url.lower():
            print("\n" + "=" * 60)
            print("LOGIN REQUIRED")
            print("Please log into LinkedIn in the browser window.")
            print("=" * 60)
            input("\nPress Enter here when you've logged in...")

            print("Navigating back to BYU alumni page...")
            driver.get(url)
            time.sleep(5)
            print(f"   Current URL: {driver.current_url}")

        # Now try to find the company filter
        print("\n5. Looking for 'Where they work' filter section...")

        # Find all fieldsets (filter sections)
        fieldsets = driver.find_elements(By.TAG_NAME, "fieldset")
        print(f"   Found {len(fieldsets)} filter sections")

        company_fieldset = None
        for fs in fieldsets:
            legends = fs.find_elements(By.TAG_NAME, "legend")
            if legends:
                legend_text = legends[0].text.strip()
                print(f"   - Filter: '{legend_text}'")
                if "work" in legend_text.lower() or "company" in legend_text.lower():
                    company_fieldset = fs
                    print(f"     ^ This is the company filter!")

        if company_fieldset:
            print("\n6. Found company filter! Looking for Add button...")
            add_btn = company_fieldset.find_elements(By.XPATH, ".//button")
            print(f"   Found {len(add_btn)} buttons in this section")

            if add_btn:
                print("   Clicking the button...")
                add_btn[0].click()
                time.sleep(2)

                print("\n7. Looking for search input...")
                inputs = driver.find_elements(By.XPATH, "//input[@placeholder]")
                for inp in inputs:
                    placeholder = inp.get_attribute("placeholder")
                    print(f"   - Input with placeholder: '{placeholder}'")

                # Try to find and fill the company search
                company_input = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'company') or contains(@placeholder, 'Company')]")
                if company_input:
                    print("\n8. Found company input! Typing 'Deloitte'...")
                    company_input[0].send_keys("Deloitte")
                    time.sleep(3)

                    # Look for dropdown results
                    print("9. Looking for dropdown results...")
                    results = driver.find_elements(By.XPATH, "//div[contains(@class, 'typeahead')]//li | //ul[contains(@role, 'listbox')]//li")
                    print(f"   Found {len(results)} results")

                    if results:
                        print("   Clicking first result...")
                        results[0].click()
                        time.sleep(2)

                        print(f"\n   *** Current URL: {driver.current_url}")

                        # Extract company ID from URL
                        import re
                        match = re.search(r'facetCurrentCompany=(\d+)', driver.current_url)
                        if match:
                            company_id = match.group(1)
                            print(f"\n   SUCCESS! Found Deloitte company ID: {company_id}")
                        else:
                            print("   Could not find company ID in URL")

        print("\n" + "=" * 60)
        print("Test complete! Browser will close in 30 seconds.")
        print("(or press Ctrl+C to close now)")
        print("=" * 60)
        time.sleep(30)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to close browser...")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
