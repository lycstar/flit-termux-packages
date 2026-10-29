"""Exercise bootstrap selection against a local synthetic APT repository."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('check_bootstrap', ROOT / 'scripts/flit/check-bootstrap.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


@unittest.skipUnless(shutil.which('apt-get'), 'APT validation requires a Linux host')
class BootstrapDependencyTests(unittest.TestCase):
    def test_real_solver_rejects_contaminated_bootstrap(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            index = root / 'Packages'
            records = []
            for name in ['bash', 'openjdk-17', 'git', 'gh', 'which', 'xz-utils']:
                records.append(f'Package: {name}\nVersion: 1\nArchitecture: aarch64\n'
                               f'Filename: {name}.deb\nSize: 1\nDescription: fixture\n')
            index.write_text('\n'.join(records) + '\n')
            archive = root / 'bootstrap.zip'
            installed = ('Package: bash\nVersion: 1\nArchitecture: aarch64\n'
                         'Status: install ok installed\nDescription: fixture\n\n')
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr('var/lib/dpkg/status', installed)
            CHECK.check(archive, index)
            with zipfile.ZipFile(archive, 'w') as bundle:
                bundle.writestr('var/lib/dpkg/status', installed +
                                'Package: dpkg-perl\nVersion: 1\nArchitecture: all\n'
                                'Status: install ok installed\nDepends: clang\nDescription: fixture\n\n')
            with self.assertRaises(subprocess.CalledProcessError):
                CHECK.check(archive, index)
