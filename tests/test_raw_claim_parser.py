import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from unclaimed_funds_lead_tool import build_lead_dataframe, read_raw_claim_text, write_browser_outputs


RAW_CLAIM_TEXT = """
Reported Owner / Payee
KONA REEF HOLDINGS LLC
75-123 ALII DR
KAILUA KONA HI 96740
FIRST HAWAIIAN BANK
$1,008.00
--

KONA REEF HLDGS LLC
75-123 ALII DRIVE
KAILUA-KONA HAWAII
BANK OF HAWAII
$850.00
--

MARIA A SANTOS
JOSE SANTOS
123 ALA MOANA BLVD APT 4
HONOLULU HI 96813
ABC INSURANCE CO
$1,450.25
64.000

ESTATE OF KEALOHA WONG
C/O LANI WONG
PO BOX 100
WAILUKU HI 96793
CIRCUIT COURT
$980.00
--
"""


class RawClaimParserTest(unittest.TestCase):
    def test_raw_claim_text_generates_browser_outputs(self):
        raw_df = read_raw_claim_text(RAW_CLAIM_TEXT)
        self.assertEqual(len(raw_df), 4)
        self.assertIn("Reported Owner", raw_df.columns)
        self.assertIn("Cash Amount", raw_df.columns)

        lead_df = build_lead_dataframe(raw_df, fuzzy_threshold=85)
        kona = lead_df[lead_df["Reported Owner"].str.startswith("KONA REEF")]
        self.assertEqual(len(kona), 2)
        self.assertEqual(kona["Group ID"].nunique(), 1)
        self.assertAlmostEqual(float(kona.iloc[0]["Grouped Total Cash"]), 1858.0)
        self.assertAlmostEqual(float(kona.iloc[0]["Estimated Recovery Fee 20%"]), 371.6)
        self.assertEqual(set(kona["Priority"]), {"Medium"})

        maria = lead_df[lead_df["Reported Owner"] == "MARIA A SANTOS"].iloc[0]
        self.assertEqual(maria["Co-owner"], "JOSE SANTOS")
        self.assertIn("securities/shares", maria["Lead Type Tags"])
        self.assertAlmostEqual(float(maria["Estimated Recovery Fee 20%"]), 290.05)

        with TemporaryDirectory() as tmpdir:
            report_path, sections = write_browser_outputs(lead_df, Path(tmpdir))
            self.assertTrue(report_path.exists())
            html = report_path.read_text(encoding="utf-8")
            self.assertIn("Securities/Shares", html)
            self.assertIn("$1,000+ Grouped Owners", html)
            csv_names = {section.filename for section in sections}
            self.assertIn("securities_shares.csv", csv_names)
            self.assertTrue((Path(tmpdir) / "all_cleaned_records.csv").exists())


if __name__ == "__main__":
    unittest.main()
