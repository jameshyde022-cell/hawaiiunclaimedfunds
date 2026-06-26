# Hawaii Auto Body Lead List Tool

This local tool creates a CSV lead list for Hawaii auto body, collision repair, paint/body, towing, and auto repair businesses.

It does not scrape or automate the State of Hawaii unclaimed-property website. If that site presents CAPTCHA or other anti-automation controls, complete those searches manually and paste your results back into the CSV.

## Files

- `leads_auto_body_hawaii.csv` - clean spreadsheet template.
- `google_places_auto_body_leads.py` - optional Google Places API script.

## CSV Fields

- Business Name
- Category
- Address
- City
- Phone
- Website
- Google Maps URL
- Source
- State Unclaimed Property Search Completed
- Total Found
- Number of Records
- Priority
- Notes

## Search Queries

The script searches:

- auto body shop Honolulu
- collision repair Honolulu
- auto paint Honolulu
- towing Honolulu
- auto body Kapolei
- auto body Waipahu
- auto body Pearl City
- auto body Aiea
- auto body Kaneohe
- auto body Kailua
- auto body Mililani
- auto body Ewa Beach
- auto body Wahiawa
- auto body Waianae

## Setup

Install Python 3 if needed. The script uses only the Python standard library.

Set a Google Places API key in PowerShell:

```powershell
$env:GOOGLE_PLACES_API_KEY="YOUR_API_KEY_HERE"
```

Run:

```powershell
python google_places_auto_body_leads.py
```

The script writes:

```text
leads_auto_body_hawaii.csv
```

If no API key is available, the script writes a blank CSV template with the correct headers.

## Manual State Search Workflow

1. Generate or open `leads_auto_body_hawaii.csv`.
2. For each business, manually search the official State of Hawaii unclaimed-property search page.
3. Do not automate the search if CAPTCHA is present.
4. Fill in:
   - `State Unclaimed Property Search Completed`
   - `Total Found`
   - `Number of Records`
   - `Priority`
   - `Notes`

Recommended values:

- `State Unclaimed Property Search Completed`: `Yes` or `No`
- `Priority`: `High`, `Medium`, or `Low`

## Notes

Google Places API usage may incur Google Cloud charges depending on your account and quota. Review your Google Cloud billing settings before running large searches.
