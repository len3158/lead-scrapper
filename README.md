# Lead Scrapper

A small Selenium script that scrapes contact rows (name, title, company,
email, LinkedIn URL, phone) from a filtered search results page on a
lead-gen platform and appends them to a CSV file, paginating automatically.

> Adapted from a technique shown in a public YouTube tutorial on scraping
> leads from a sales-intelligence platform. Shared here as a personal
> reference implementation.

## Requirements

- Python 3.9+
- Google Chrome
- [chromedriver](https://chromedriver.chromium.org/downloads) matching your
  installed Chrome version
- An active account on the target lead platform

Install the Python dependency:

```bash
pip install -r requirements.txt
```

## Setup

1. Download chromedriver and note its path (or place it next to the script
   and set `CHROME_DRIVER_PATH=./chromedriver`).
2. Set the environment variables below, or edit the defaults directly at the
   top of `lead_scraper.py`:

   | Variable | Description |
   |---|---|
   | `CHROME_USER_DATA_DIR` | Path to your Chrome profile directory, so the script reuses your logged-in session |
   | `CHROME_DRIVER_PATH` | Path to the chromedriver binary |
   | `SEARCH_URL` | Your filtered search results URL |
   | `CSV_OUTPUT` | Output CSV filename (defaults to `leads.csv`) |

3. The first time you run it, log in to your lead platform manually in the
   Chrome window that opens — the session will persist in your Chrome
   profile for future runs.

## Usage

```bash
export CHROME_USER_DATA_DIR="/Users/you/Library/Application Support/Google/Chrome"
export CHROME_DRIVER_PATH="./chromedriver"
export SEARCH_URL="https://your-lead-platform.example/search?..."

python lead_scraper.py
```

Captured rows are appended to `leads.csv` (or your configured output file) as
the script goes: `first_name, last_name, job_title, company_name, email_1,
email_2, linkedin_url, phone_number`.

## Notes

- This relies on the target platform's current DOM structure/CSS class
  names, which can change at any time — selectors may need updating if the
  platform ships a UI change.
- Respect the target platform's Terms of Service and any applicable data
  protection regulations (e.g. GDPR) when scraping and storing contact data.

## License

MIT — see [LICENSE](LICENSE).
