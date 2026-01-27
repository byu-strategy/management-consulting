#!/usr/bin/env python3
"""
LinkedIn Company ID Lookup Script

Automates looking up LinkedIn company IDs for consulting firms
by using the BYU alumni page's company filter.

Requirements:
    pip install selenium webdriver-manager

Usage:
    python lookup_linkedin_ids.py           # Process all firms
    python lookup_linkedin_ids.py --limit 3 # Test with 3 firms
"""

import argparse
import json
import time
import re
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
FIRMS_FILE = DATA_DIR / "firms-to-research.json"
PROFILE_DIR = SCRIPT_DIR / ".chrome_profile"

# LinkedIn URLs
BYU_ALUMNI_URL = "https://www.linkedin.com/school/brigham-young-university/people/"


def setup_driver():
    """Set up Chrome driver with dedicated profile."""
    options = Options()

    # Use a dedicated profile directory (avoids conflicts with main Chrome)
    PROFILE_DIR.mkdir(exist_ok=True)
    options.add_argument(f"--user-data-dir={PROFILE_DIR}")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    # Disable automation detection
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def load_firms():
    """Load firms from JSON file."""
    with open(FIRMS_FILE, "r") as f:
        return json.load(f)


def save_firms(firms):
    """Save firms back to JSON file."""
    with open(FIRMS_FILE, "w") as f:
        json.dump(firms, f, indent=2)
    print(f"   Saved to {FIRMS_FILE.name}")


def extract_company_id_from_url(url):
    """Extract company ID from LinkedIn URL with facetCurrentCompany parameter."""
    match = re.search(r'facetCurrentCompany=(\d+)', url)
    if match:
        return int(match.group(1))
    return None


def clear_company_filter(driver):
    """Clear any existing company filter to reset for next search."""
    try:
        # Look for "Clear" or "X" button in the filter area
        clear_buttons = driver.find_elements(By.XPATH, "//button[contains(@aria-label, 'Remove') or contains(@aria-label, 'Clear')]")
        for btn in clear_buttons:
            try:
                btn.click()
                time.sleep(0.5)
            except:
                pass
    except:
        pass

    # Navigate back to base URL to fully reset
    driver.get(BYU_ALUMNI_URL)
    time.sleep(3)


def lookup_company_id(driver, firm_name):
    """
    Look up a company's LinkedIn ID using the BYU alumni page search.
    Types firm name in search, selects first dropdown result, extracts ID from URL.
    Returns the company ID (int) or None if not found.
    """
    try:
        # Reset to base URL
        driver.get(BYU_ALUMNI_URL)
        time.sleep(3)

        # Find the alumni search textarea by ID
        search_input = driver.find_element(By.ID, "people-search-keywords")

        if not search_input:
            print("   Could not find alumni search input")
            return None

        # Clear and type the firm name
        search_input.click()
        time.sleep(0.5)
        search_input.clear()
        search_input.send_keys(firm_name)
        time.sleep(2.5)  # Wait for autocomplete dropdown

        # Look for dropdown results
        results = driver.find_elements(By.XPATH,
            "//div[contains(@class, 'typeahead')]//li | "
            "//ul[contains(@role, 'listbox')]//li | "
            "//div[contains(@class, 'basic-typeahead')]//div[contains(@class, 'result')] | "
            "//div[contains(@class, 'search-typeahead')]//li | "
            "//div[contains(@class, 'autocomplete')]//li")

        if not results:
            print(f"   No autocomplete results for '{firm_name}'")
            search_input.send_keys(Keys.ESCAPE)
            return None

        # Click the first result
        print(f"   Found {len(results)} results, clicking first...")
        results[0].click()
        time.sleep(2)

        # Extract company ID from URL
        current_url = driver.current_url
        company_id = extract_company_id_from_url(current_url)

        return company_id

    except Exception as e:
        print(f"   Error: {e}")
        return None


def check_login(driver):
    """Check if logged into LinkedIn, prompt for login if needed."""
    driver.get(BYU_ALUMNI_URL)
    time.sleep(3)

    current_url = driver.current_url.lower()
    if "login" in current_url or "signin" in current_url or "checkpoint" in current_url:
        print("\n" + "=" * 60)
        print("LOGIN REQUIRED")
        print("Please log into LinkedIn in the browser window.")
        print("=" * 60)
        input("\nPress Enter here when you've logged in...")

        driver.get(BYU_ALUMNI_URL)
        time.sleep(3)

        # Check again
        if "login" in driver.current_url.lower():
            print("Still not logged in. Please try again.")
            return False

    print("   Logged into LinkedIn ✓")
    return True


def main():
    """Main function to look up company IDs."""
    parser = argparse.ArgumentParser(description="Look up LinkedIn company IDs for consulting firms")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of firms to process (for testing)")
    args = parser.parse_args()

    print("=" * 60)
    print("LinkedIn Company ID Lookup")
    print("=" * 60)

    # Load firms
    firms = load_firms()
    print(f"\nLoaded {len(firms)} firms from {FIRMS_FILE.name}")

    # Filter to firms without linkedin_id
    firms_to_lookup = [f for f in firms if f.get("linkedin_id") is None]
    print(f"Found {len(firms_to_lookup)} firms without linkedin_id")

    if args.limit:
        firms_to_lookup = firms_to_lookup[:args.limit]
        print(f"Limited to {args.limit} firms for testing")

    if not firms_to_lookup:
        print("\nAll firms already have linkedin_id. Nothing to do.")
        return

    # Set up browser
    print("\nStarting Chrome browser...")
    driver = setup_driver()

    try:
        # Check login
        print("\nChecking LinkedIn login...")
        if not check_login(driver):
            return

        # Process each firm
        found_count = 0
        not_found = []

        for i, firm in enumerate(firms_to_lookup):
            firm_name = firm["name"]
            print(f"\n[{i+1}/{len(firms_to_lookup)}] {firm_name}")

            company_id = lookup_company_id(driver, firm_name)

            if company_id:
                firm["linkedin_id"] = company_id
                found_count += 1
                print(f"   ✓ Found ID: {company_id}")
                save_firms(firms)
            else:
                not_found.append(firm_name)
                print(f"   ✗ Not found")

            # Be polite to LinkedIn
            time.sleep(2)

        # Summary
        print("\n" + "=" * 60)
        print(f"Complete! Found {found_count}/{len(firms_to_lookup)} company IDs")

        if not_found:
            print(f"\nCould not find IDs for:")
            for name in not_found:
                print(f"   - {name}")

        print(f"\nResults saved to {FIRMS_FILE}")
        print("=" * 60)

    finally:
        print("\nClosing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
