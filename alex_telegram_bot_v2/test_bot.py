#!/usr/bin/env python3
"""Test script for UID detection"""

import re
import unittest

class TestUIDDetection(unittest.TestCase):
    def setUp(self):
        self.uid_pattern = re.compile(r'\b(?:uid\s*)?([0-9]{8})\b', re.IGNORECASE)

    def extract_uid(self, text):
        match = self.uid_pattern.search(text)
        return match.group(1) if match else None

    def test_valid_uids(self):
        test_cases = [
            ("12345678", "12345678"),
            ("UID 12345678", "12345678"),
            ("uid 12345678", "12345678"),
            ("Mi UID es 12345678", "12345678"),
        ]

        for text, expected in test_cases:
            result = self.extract_uid(text)
            self.assertEqual(result, expected, f"Failed for: {text}")

    def test_invalid_uids(self):
        invalid_cases = ["1234567", "123456789", "abcd1234", ""]

        for text in invalid_cases:
            result = self.extract_uid(text)
            self.assertIsNone(result, f"Should be invalid: {text}")

if __name__ == "__main__":
    print("🧪 Running UID Detection Tests...")
    unittest.main(verbosity=2)
