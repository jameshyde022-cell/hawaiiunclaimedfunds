# Hawaii Unclaimed Funds Lead Workbook Tool

This local Python tool turns scraped or pasted Hawaii unclaimed-property records into an Excel workbook of leads.

It does not scrape websites, bypass CAPTCHA, submit searches, or claim that any person is the correct contact. It only cleans data, groups likely related records, creates research links, and marks every output row as `Needs Human Verification`.

## Files

- `unclaimed_funds_lead_tool.py` - workbook generator.
- `requirements-unclaimed-funds-tool.txt` - Python dependencies.
- `sample_unclaimed_records.csv` - sample input for testing.

## Setup

From PowerShell in this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-unclaimed-funds-tool.txt
```

## Run

Create a workbook from CSV:

```powershell
python unclaimed_funds_lead_tool.py sample_unclaimed_records.csv -o hawaii_unclaimed_funds_leads.xlsx
```

Create a workbook from Excel:

```powershell
python unclaimed_funds_lead_tool.py scraped_records.xlsx -o leads.xlsx
```

Create a workbook from pasted text saved in a `.txt` file:

```powershell
python unclaimed_funds_lead_tool.py pasted_records.txt --pasted-text -o leads.xlsx
```

The pasted text can be comma-delimited or tab-delimited with a header row.

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

## Workbook Tabs

- `All Cleaned Records`
- `$1,000+ Single Claims`
- `$1,000+ Grouped Owners`
- `High Priority Leads`
- `Business Leads`
- `Co-owner Complex Claims`
- `Research Queue`
- `Summary Dashboard`

Excel limits worksheet names to 31 characters, so `Co-owner / Complex Claims` is exported as `Co-owner Complex Claims`.

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
