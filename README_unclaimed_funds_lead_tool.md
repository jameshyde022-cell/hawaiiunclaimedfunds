# Hawaii Unclaimed Funds Lead Workbook Tool

This local Python tool turns scraped or pasted Hawaii unclaimed-property records into browser-viewable HTML, per-section CSV files, and optional Excel workbooks.

It does not scrape websites, bypass CAPTCHA, submit searches, or claim that any person is the correct contact. It only cleans data, groups likely related records, creates research links, and marks every output row as `Needs Human Verification`.

## Files

- `unclaimed_funds_lead_tool.py` - report generator.
- `local_claim_processor_app.py` - local browser paste-and-process interface.
- `requirements-unclaimed-funds-tool.txt` - Python dependencies.
- `sample_unclaimed_records.csv` - sample input for testing.

## Setup

From PowerShell in this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-unclaimed-funds-tool.txt
```


## Local Browser App

For normal use, start the local paste-and-process page:

```powershell
python local_claim_processor_app.py
```

It opens `http://127.0.0.1:8765/` in your browser. Paste raw copied claim text from the Hawaii unclaimed-property site into the text box and click `Process`. The app writes the browser report and CSV files to:

```text
C:\tmp\my_claim_report
```

Open `C:\tmp\my_claim_report\lead_report.html` first. The tool parses raw claim blocks with multiline owner/payee names, multiline addresses, reporting companies, cash amounts such as `$1,008.00`, and shares such as `64.000` or `--`.

## Run

Create a browser report and CSV files from CSV:

```powershell
python unclaimed_funds_lead_tool.py sample_unclaimed_records.csv --output-dir C:\tmp\unclaimed_funds_output
```

Create the same browser/CSV outputs from Excel:

```powershell
python unclaimed_funds_lead_tool.py scraped_records.xlsx --output-dir leads_output
```

Create browser/CSV outputs from pasted text saved in a `.txt` file:

```powershell
python unclaimed_funds_lead_tool.py pasted_records.txt --pasted-text --output-dir leads_output
```

The pasted text can be comma-delimited or tab-delimited with a header row.

To also create an Excel workbook, add `--xlsx`, or pass a workbook path with `-o`:

```powershell
python unclaimed_funds_lead_tool.py sample_unclaimed_records.csv --output-dir leads_output --xlsx
python unclaimed_funds_lead_tool.py sample_unclaimed_records.csv --output-dir leads_output -o leads.xlsx
```

## Accepted Columns

The tool recognizes common variants of these columns:

- `Reported Owner`
- `Co-owner`
- `Address / Location`
- `Reporting Company`
- `Cash Amount`
- `Shares`
- `Property ID`
- `Source`

Missing optional columns are created as blanks.

## Report Sections

- `Summary Dashboard`
- `High Priority Leads`
- `Business Leads`
- `$1,000+ Single Claims`
- `$1,000+ Grouped Owners`
- `Co-owner Complex Claims`
- `Securities/Shares`
- `Research Queue`
- `All Cleaned Records`

The main browser file is `lead_report.html`. The tool also writes one CSV per section, including `high_priority_leads.csv`, `business_leads.csv`, and `all_cleaned_records.csv`.

## Lead Logic

- Owner names are normalized by uppercasing, removing punctuation, and stripping common honorific/name noise.
- Likely same-owner groups are created with fuzzy matching using `rapidfuzz`.
- Single records with `Cash Amount >= $1,000` appear on the single-claims tab.
- Owner groups with total cash `>= $1,000` appear on the grouped-owners tab.
- Estimated recovery fee is calculated as 20% of the grouped total.
- Priority is:
  - `High` for grouped total `>= $5,000`
  - `Medium` for grouped total `$1,000-$4,999`
  - `Low` under `$1,000`
  - `Low - grouped` under `$1,000` when multiple records were grouped

## Tags and Research Steps

The tool adds lead type tags including:

- `business`
- `individual`
- `co-owner`
- `government`
- `escrow/trust`
- `insurance-related`
- `bank/CD`
- `court-related`

The `Research Needed` column suggests steps such as checking Hawaii DCCA, finding a registered agent, verifying business status, finding an owner or manager, searching a company website, searching LinkedIn, verifying addresses, and calling State Unclaimed Property for document requirements.

## Fuzzy Matching

Default fuzzy threshold is `90`. Lower it only when you want more aggressive grouping:

```powershell
python unclaimed_funds_lead_tool.py scraped_records.csv --fuzzy-threshold 85 -o leads.xlsx
```

Always review the `Group Confidence`, `Normalized Owner`, and `Needs Human Verification` columns before using the leads.

## Compliance Notes

- Do not automate or bypass CAPTCHA-protected sites.
- Do not treat search links as proof of identity.
- Do not claim a person is the correct contact unless your human research verifies it.
- Use generated DCCA and Google links only as starting points for manual research.
