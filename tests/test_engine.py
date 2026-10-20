"""
Unit tests for SlothDesk AI Engine & Extractor.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import tempfile
from sloth_core.extractor import extract_content
from sloth_core.engine import SlothAIEngine

class TestSlothEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SlothAIEngine()

    def test_text_extractor(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".txt", delete=False) as f:
            f.write("INVOICE #994\nTotal Due: $42.00 USD\nPayment date: Nov 1")
            tmp_path = Path(f.name)

        try:
            content, meta = extract_content(tmp_path)
            self.assertIn("INVOICE", content)
            self.assertEqual(meta["extension"], ".txt")
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_embedded_nlp_finance_categorization(self):
        filename = "receipt_october_coffee.csv"
        content = "Item,Price\nLatte,5.50\nTotal,$5.50 USD\nPayment,Paid"
        meta = {"extension": ".csv", "size_bytes": len(content)}

        summary = self.engine.analyze_file(filename, content, meta)
        self.assertEqual(summary.category, "finance")
        self.assertIn("5.50", summary.one_liner)
        self.assertTrue(any(t in summary.tags for t in ["finance", "receipt", "csv"]))

    def test_embedded_nlp_code_categorization(self):
        filename = "script.py"
        content = "import os\ndef calculate():\n    return 42"
        meta = {"extension": ".py", "size_bytes": len(content)}

        summary = self.engine.analyze_file(filename, content, meta)
        self.assertEqual(summary.category, "code")
        self.assertTrue(summary.suggested_filename.endswith(".py"))

if __name__ == "__main__":
    unittest.main()
