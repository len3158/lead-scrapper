"""
Lead Scraper
============
Scrapes contact rows (name, title, company, email, LinkedIn, phone) from an
already-filtered search results page on a lead-gen platform and appends them
to a CSV file.

Adapted from a technique popularized in a public YouTube tutorial on
scraping leads from a sales-intelligence platform. Shared here for
personal/educational reference.

Requirements:
  pip install selenium
  A matching chromedriver binary for your installed Chrome version
  (https://chromedriver.chromium.org/downloads), placed per CHROME_DRIVER_PATH below.

Setup:
  1. Fill in CHROME_USER_DATA_DIR below with your own Chrome profile path.
  2. Run this script once and manually log in to your lead platform of
     choice in the opened Chrome window so the session is saved to that
     profile.
  3. Set SEARCH_URL to your filtered search results page.
  4. Run again — it will scroll/paginate the results and export matches.

Usage:
  python lead_scraper.py
"""

import os
import re
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# ──────────────────────────────────────────────
#  CONFIGURATION — edit these before running
# ──────────────────────────────────────────────

# Path to your Chrome user profile (so the scraper reuses your logged-in session).
# macOS example: "/Users/<you>/Library/Application Support/Google/Chrome"
# Windows example: r"C:\Users\<you>\AppData\Local\Google\Chrome\User Data"
CHROME_USER_DATA_DIR = os.environ.get("CHROME_USER_DATA_DIR", "<path-to-your-chrome-profile>")

# Path to your chromedriver executable
CHROME_DRIVER_PATH = os.environ.get("CHROME_DRIVER_PATH", "./chromedriver")

# Your filtered search results URL (already filtered to the leads you want)
SEARCH_URL = os.environ.get("SEARCH_URL", "<your-search-results-url>")

# Output CSV file
CSV_FILE_NAME = os.environ.get("CSV_OUTPUT", "leads.csv")

# Domain(s) to exclude from scraped emails (e.g. tracking/placeholder domains)
EXCLUDED_EMAIL_DOMAIN = "sentry.io"

# ──────────────────────────────────────────────
#  SCRAPER
# ──────────────────────────────────────────────

chrome_options = Options()
chrome_options.add_argument(f"user-data-dir={CHROME_USER_DATA_DIR}")
service = Service(CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get(SEARCH_URL)
time.sleep(2)


def find_email_address(page_source):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.findall(email_pattern, page_source)


def filter_emails(emails, excluded_domain):
    filtered = [email for email in emails if not email.endswith(excluded_domain)]
    return filtered[:2]


def split_name(name):
    parts = name.split()
    first_name = parts[0] if parts else ''
    last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''
    return first_name, last_name


def main():
    while True:
        try:
            loaded_section_selector = "[data-cy-loaded='true']"
            loaded_section = driver.find_element(By.CSS_SELECTOR, loaded_section_selector)

            tbodies = loaded_section.find_elements(By.TAG_NAME, 'tbody')
            if not tbodies:
                break

            for tbody in tbodies:
                first_anchor_text = tbody.find_element(By.TAG_NAME, 'a').text
                first_name, last_name = split_name(first_anchor_text)

                linkedin_url = ''
                for link in tbody.find_elements(By.TAG_NAME, 'a'):
                    href = link.get_attribute('href')
                    if href and 'linkedin.com' in href:
                        linkedin_url = href
                        break

                job_title_element = tbody.find_element(By.CLASS_NAME, 'zp_Y6y8d')
                job_title = job_title_element.text if job_title_element else ''

                company_name = ''
                for link in tbody.find_elements(By.TAG_NAME, 'a'):
                    href = link.get_attribute('href')
                    if href and 'accounts' in href:
                        company_name = link.text
                        break

                phone_number = tbody.find_elements(By.TAG_NAME, 'a')[-1].text

                button_classes = ["zp-button", "zp_zUY3r", "zp_hLUWg", "zp_n9QPr", "zp_B5hnZ", "zp_MCSwB", "zp_IYteB"]

                try:
                    button = tbody.find_element(By.CSS_SELECTOR, "." + ".".join(button_classes))
                    if button:
                        button.click()
                        email_addresses = find_email_address(driver.page_source)
                        filtered_emails = filter_emails(email_addresses, EXCLUDED_EMAIL_DOMAIN)
                        with open(CSV_FILE_NAME, 'a', newline='', encoding='utf-8') as file:
                            writer = csv.writer(file)
                            print(f"{first_name} captured")
                            if len(filtered_emails) == 1:
                                writer.writerow([first_name, last_name, job_title, company_name, filtered_emails[0], '', linkedin_url, phone_number])
                            elif len(filtered_emails) == 2:
                                writer.writerow([first_name, last_name, job_title, company_name, filtered_emails[0], filtered_emails[1], linkedin_url, phone_number])
                        button.click()
                        tbody_height = driver.execute_script("return arguments[0].offsetHeight;", tbody)
                        driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", loaded_section, tbody_height)
                except NoSuchElementException:
                    continue

            # Pagination
            next_button_selector = ".zp-button.zp_zUY3r.zp_MCSwB.zp_xCVC8[aria-label='right-arrow']"
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, next_button_selector)
                next_button.click()
                time.sleep(1)
            except NoSuchElementException:
                print("No more pages to navigate.")
                break

        except Exception as e:
            error_message = str(e)
            if "element click intercepted" in error_message:
                print("Done — leads are ready.")
                break
            else:
                print(f"An error occurred: {error_message}")
                break

    driver.quit()


if __name__ == "__main__":
    main()
