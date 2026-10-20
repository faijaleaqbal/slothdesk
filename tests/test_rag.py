"""
Unit tests for SlothDesk Local RAG engine.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import tempfile
import shutil
from sloth_core.organizer import SlothOrganizer
from sloth_core.rag import SlothRAG

class TestSlothRAG(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_sloth.db"
        self.organizer = SlothOrganizer(db_path=self.db_path)
        self.rag = SlothRAG(self.organizer)

    def tearDown(self):
        import gc
        gc.collect()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_search_and_ask(self):
        # Create and organize 2 files
        f1 = self.temp_dir / "aws_cloud_statement.txt"
        f1.write_text("Amazon Web Services Invoice. S3 bucket costs $45.20. Total due $50.")
        self.organizer.organize_file(f1, copy_mode=False)

        f2 = self.temp_dir / "grocery_list.txt"
        f2.write_text("Buy oat milk, bananas, and sourdough bread.")
        self.organizer.organize_file(f2, copy_mode=False)

        # Search for AWS
        matches = self.rag.search_files("AWS S3 costs", top_k=2)
        self.assertGreater(len(matches), 0)
        self.assertIn("aws", matches[0]["name"].lower())

        # Ask question
        res = self.rag.ask("What are my AWS S3 costs?")
        self.assertIn("answer", res)
        self.assertGreater(len(res["matched_files"]), 0)

if __name__ == "__main__":
    unittest.main()
