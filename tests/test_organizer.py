"""
Unit tests for SlothDesk Organizer & Undo mechanism.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import unittest
import tempfile
import shutil
from sloth_core.organizer import SlothOrganizer

class TestSlothOrganizer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_sloth.db"
        self.organizer = SlothOrganizer(db_path=self.db_path)

    def tearDown(self):
        import gc
        gc.collect()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_organize_and_undo(self):
        # Create test incoming file
        test_file = self.temp_dir / "invoice_test.txt"
        test_file.write_text("Total Amount Due: $100.00 USD\nDue Date: Tomorrow")

        res = self.organizer.organize_file(test_file, copy_mode=False)
        self.assertTrue(res["success"])
        self.assertEqual(res["category"], "finance")
        self.assertFalse(test_file.exists())  # moved

        # Verify in database
        files = self.organizer.get_all_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]["original_name"], "invoice_test.txt")

        # Undo
        undo_res = self.organizer.undo_action(res["file_id"])
        self.assertTrue(undo_res["success"])
        self.assertTrue(test_file.exists())  # restored

        # Check files list again
        active_files = self.organizer.get_all_files()
        self.assertEqual(len(active_files), 0)

if __name__ == "__main__":
    unittest.main()
