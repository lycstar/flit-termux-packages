"""Verify source fallbacks without network access."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
URL = 'https://pkgconfig.freedesktop.org/releases/pkg-config.tar.gz'
MIRROR = 'https://distfiles.macports.org/pkgconfig/pkg-config.tar.gz'
FINAL = 'https://cdn.NetBSD.org/pub/pkgsrc/distfiles/pkg-config.tar.gz'
GOOD = 'verified source\n'
SHA = hashlib.sha256(GOOD.encode()).hexdigest()


class SourceFallbackTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.calls = self.root / 'calls'
        self.responses = self.root / 'responses.json'
        self.dest = self.root / 'archive'
        self.executable('curl', '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
args=sys.argv[1:]
url=args[-1]
with open(os.environ['TEST_CALLS'],'a') as f:f.write(url+'\\n')
response=json.loads(Path(os.environ['TEST_RESPONSES']).read_text()).get(url)
if response is None:sys.exit(22)
Path(args[args.index('--output')+1]).write_text(response)
''')
        self.executable('sleep', '#!/bin/sh\nexit 0\n')
        self.executable('sha256sum', '''#!/usr/bin/env python3
import hashlib,sys
from pathlib import Path
print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest()+'  '+sys.argv[1])
''')
        self.env = {**os.environ, 'PATH': str(self.bin)+':'+os.environ['PATH'],
                    'TERMUX_PKG_TMPDIR': str(self.root),
                    'TEST_CALLS': str(self.calls), 'TEST_RESPONSES': str(self.responses)}

    def executable(self, name, source):
        path = self.bin / name
        path.write_text(source)
        path.chmod(0o755)

    def download(self, responses, checksum=SHA):
        self.responses.write_text(json.dumps(responses))
        return subprocess.run(['bash', '-eu', '-c',
                               '. "$1"; termux_download "$2" "$3" "$4"',
                               'test', str(ROOT / 'scripts/build/termux_download.sh'),
                               URL, str(self.dest), checksum], env=self.env,
                              text=True, capture_output=True)

    def test_original_source_is_preferred(self):
        result = self.download({URL: GOOD})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.calls.read_text().splitlines(), [URL])

    def test_missing_source_uses_checksum_verified_mirror(self):
        result = self.download({MIRROR: GOOD})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.dest.read_text(), GOOD)
        self.assertIn(MIRROR, self.calls.read_text())

    def test_corrupt_mirror_is_rejected_then_next_is_tried(self):
        result = self.download({MIRROR: 'corrupt', FINAL: GOOD})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.dest.read_text(), GOOD)
        self.assertIn(FINAL, self.calls.read_text())

    def test_all_checksum_failures_preserve_existing_destination(self):
        self.dest.write_text('existing')
        result = self.download({URL: 'bad', MIRROR: 'bad', FINAL: 'bad'})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.dest.read_text(), 'existing')

    def test_unverified_download_does_not_use_mirrors(self):
        result = self.download({MIRROR: GOOD}, checksum='SKIP_CHECKSUM')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(MIRROR, self.calls.read_text())
