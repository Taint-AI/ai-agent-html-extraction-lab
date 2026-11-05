import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import experiment as e


class ExtractionTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = e.load_fixtures()
        self.rows = {r["id"]: r for r in e.run()["rows"]}

    def test_principal_pair_loses_only_placement_in_capture(self):
        self.assertEqual(e.run()["principal_pair"], {
            "ids": ["ordinary", "hidden_attribute"], "text_only_equal": True,
            "source_html_equal": False, "source_hash_equal": False})
        a, b = self.fixtures[:2]
        self.assertEqual(a["html"].replace('<div>', '<div hidden>'), b["html"])
        self.assertEqual(self.rows["hidden_attribute"]["captures"]["text_only"], {"text": "Product: notebook. NOTE-MARKER"})

    def test_source_capture_is_original_not_reserialized(self):
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["id"]):
                cap = self.rows[fixture["id"]]["captures"]["source_linked"]
                self.assertEqual(cap["source_html"], fixture["html"])
                self.assertEqual(cap["source_sha256"], hashlib.sha256(fixture["html"].encode()).hexdigest())

    def test_same_text_in_both_captures(self):
        for row in self.rows.values():
            self.assertEqual(row["captures"]["text_only"]["text"], row["captures"]["source_linked"]["text"])

    def test_explicit_attribute_and_style_cases_keep_marker(self):
        for key in ["hidden_attribute", "nested_hidden", "inline_display_none", "css_class", "hidden_false"]:
            with self.subTest(key=key):
                self.assertEqual(self.rows[key]["captures"]["text_only"]["text"], "Product: notebook. NOTE-MARKER")

    def test_non_text_families_exclude_marker(self):
        for key in ["comment", "meta", "script", "style", "template"]:
            with self.subTest(key=key):
                self.assertEqual(self.rows[key]["captures"]["text_only"]["text"], "Product: notebook.")
                self.assertIn(e.MARKER, self.rows[key]["captures"]["source_linked"]["source_html"])

    def test_entity_decoding_does_not_change_retained_source(self):
        cap = self.rows["entity"]["captures"]["source_linked"]
        self.assertIn("NOTE&#45;MARKER", cap["source_html"])
        self.assertIn("NOTE-MARKER", cap["text"])

    def test_aria_attribute_not_interpreted_as_visual_filter(self):
        self.assertTrue(self.rows["aria_hidden"]["marker_in_extracted_text"])

    def test_benign_and_useful_text_preserved(self):
        self.assertFalse(self.rows["benign_no_marker"]["marker_in_extracted_text"])
        for row in self.rows.values():
            self.assertIn("Product: notebook.", row["captures"]["text_only"]["text"])

    def test_invalid_and_duplicate_fixtures_fail(self):
        cases = [[], {}, [self.fixtures[0], self.fixtures[0]], [{"id": "x"}]]
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "fixtures.json"
            for case in cases:
                p.write_text(json.dumps(case))
                with self.assertRaises(ValueError):
                    e.load_fixtures(p)

    def test_version_mismatch_fails(self):
        with patch("importlib.metadata.version", return_value="0"):
            with self.assertRaises(RuntimeError):
                e.verify_versions()

    def test_actual_output_mismatch_fails(self):
        with patch.object(e, "extract_text", return_value="wrong"):
            with self.assertRaises(AssertionError):
                e.run()

    def test_deterministic_and_no_network(self):
        with patch("socket.socket", side_effect=AssertionError("network")), patch("socket.getaddrinfo", side_effect=AssertionError("DNS")):
            first, second = e.run(), e.run()
        self.assertEqual(first, second)
        self.assertEqual(e.evidence(first), e.evidence(second))


if __name__ == "__main__":
    unittest.main()
