#!/usr/bin/env python3
"""Generate a flat APT index for packages stored in one Release directory."""
import email.utils
import gzip
import hashlib
import lzma
from pathlib import Path
import subprocess
import sys


def generate(directory):
    root = Path(directory).resolve()
    result = subprocess.run(['dpkg-scanpackages', '--multiversion', '.', '/dev/null'],
                            cwd=root, check=True, capture_output=True, text=True)
    lines = []
    for line in result.stdout.splitlines():
        if line.startswith('Filename: '):
            line = 'Filename: ' + Path(line.removeprefix('Filename: ')).name
        lines.append(line)
    data = ('\n'.join(lines) + '\n').encode()
    (root / 'Packages').write_bytes(data)
    (root / 'Packages.gz').write_bytes(gzip.compress(data, mtime=0))
    (root / 'Packages.xz').write_bytes(lzma.compress(data))
    release = ['Origin: Flit', 'Label: Flit', 'Suite: stable',
               'Date: ' + email.utils.formatdate(usegmt=True),
               'Architectures: aarch64 all', 'Description: Flit aarch64 packages']
    for header, algorithm in [('MD5Sum', 'md5'), ('SHA256', 'sha256'), ('SHA512', 'sha512')]:
        release.append(header + ':')
        for name in ['Packages', 'Packages.gz', 'Packages.xz']:
            contents = (root / name).read_bytes()
            release.append(f' {hashlib.new(algorithm, contents).hexdigest()} {len(contents)} {name}')
    (root / 'Release').write_text('\n'.join(release) + '\n')


if __name__ == '__main__':
    generate(sys.argv[1])
