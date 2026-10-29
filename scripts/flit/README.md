# Flit runtime distribution

Package compilation uses the official source builder for `cc.lycstar.flit` and
Android aarch64. Source downloads retain checksum-verified mirror fallbacks.
`publish-packages.sh` merges existing Release assets with new packages and updates
the flat APT metadata after publishing the package files.

Bootstrap generation uses the official `generate-bootstraps.sh` against the
published `pool` Release with `--repository-layout flat`. It recursively selects
runtime dependencies and verifies package SHA-256 digests. It must not assemble
all files emitted by the source builder: those include development subpackages
whose dependencies were not built for the bootstrap.

`check-bootstrap.py` checks the resulting installed-package database with a real,
isolated APT solver, then simulates installation of OpenJDK, Git and GitHub CLI.
The same check runs before publishing the bootstrap. No target binaries run on
the build host. Missing or conflicting dependencies fail publication.

To generate a bootstrap, first publish required packages with the `packages`
workflow target, then run `bootstrap`. Bootstrap generation reuses published
binaries; it does not need to recompile them. Source-build smoke tests run first.
