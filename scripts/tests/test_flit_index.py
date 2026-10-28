"""Validate the filenames and final Release checksums of a flat APT index."""
import gzip
import hashlib
import importlib.util
import lzma
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    'flit_index', Path(__file__).resolve().parents[1] / 'flit/generate-index.py')
INDEX = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INDEX)


class FlatIndexTests(unittest.TestCase):
    def test_release_checksums_match_final_relative_indexes(self):
        listing = ('Package: hello\nVersion: 1.0\nArchitecture: aarch64\n'
                   'Filename: ./hello_1.0_aarch64.deb\nSize: 1\n\n')
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(INDEX.subprocess, 'run', return_value=
                              subprocess.CompletedProcess([], 0, stdout=listing)):
                INDEX.generate(tmp)
            root = Path(tmp)
            packages = (root / 'Packages').read_bytes()
            self.assertIn(b'Filename: hello_1.0_aarch64.deb', packages)
            self.assertNotIn(b'Filename: ./', packages)
            self.assertEqual(gzip.decompress((root / 'Packages.gz').read_bytes()), packages)
            self.assertEqual(lzma.decompress((root / 'Packages.xz').read_bytes()), packages)
            release = (root / 'Release').read_text()
            for name in ['Packages', 'Packages.gz', 'Packages.xz']:
                data = (root / name).read_bytes()
                self.assertIn(f'{hashlib.sha256(data).hexdigest()} {len(data)} {name}', release)
            self.assertIn('Date: ', release)
