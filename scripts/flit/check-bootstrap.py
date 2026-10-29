#!/usr/bin/env python3
"""Validate installed bootstrap dependencies and simulate the app's APT installs.

Uses the real APT solver with isolated state; never installs or executes target
binaries and never reads the host's installed-package database or repositories.
"""
import getpass
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def check(archive, index):
    with zipfile.ZipFile(archive) as bundle:
        status = bundle.read('var/lib/dpkg/status')
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        repo = root / 'repo'
        repo.mkdir()
        (repo / 'Packages').write_bytes(Path(index).read_bytes())
        (root / 'status').write_bytes(status)
        (root / 'sources.list').write_text(f'deb [trusted=yes] file:{repo} ./\n')
        for name in ['lists/partial', 'cache/archives/partial', 'etc']:
            (root / name).mkdir(parents=True, exist_ok=True)
        config = root / 'apt.conf'
        config.write_text(f'''
#clear APT::Architectures;
APT::Architecture "aarch64";
APT::Architectures {{ "aarch64"; }};
APT::Sandbox::User "{getpass.getuser()}";
Dir::State::status "{root / 'status'}";
Dir::State::lists "{root / 'lists'}";
Dir::Cache "{root / 'cache'}";
Dir::Etc::sourcelist "{root / 'sources.list'}";
Dir::Etc::sourceparts "-";
Dir::Etc::parts "-";
Dir::Etc::main "-";
Dir::Etc::preferences "{root / 'etc/preferences'}";
Dir::Etc::preferencesparts "-";
Debug::NoLocking "true";
''')
        base = ['apt-get']
        environment = {**os.environ, 'APT_CONFIG': str(config)}
        subprocess.run(base + ['update'], check=True, env=environment)
        subprocess.run(base + ['check'], check=True, env=environment)
        subprocess.run(base + ['--simulate', '--no-install-recommends',
                               'install', 'openjdk-17', 'git', 'gh', 'which', 'xz-utils'], check=True, env=environment)
        print('Bootstrap dependency check and development-tool installation simulation passed.')


if __name__ == '__main__':
    check(*sys.argv[1:])
