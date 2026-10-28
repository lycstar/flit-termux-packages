# Flit toolchain distribution

This repository contains an upstream Termux packages source snapshot adapted for Flit. Upstream licenses, copyright notices, and package metadata are retained.

- Upstream: https://github.com/termux/termux-packages
- Source revision: `4e81bc83267eb71e4c5c2c1c9d9a1be88ffabb71`
- Android application ID and namespace: `cc.lycstar.flit`
- Installation prefix: `/data/data/cc.lycstar.flit/files/usr`
- Target architecture: `aarch64`

## Build

Run **Build Flit toolchain** manually in Actions. The `hello` package and its dependencies are built and checked before any bootstrap or development packages. Select `smoke` to run only that test.

The workflow uses the official Termux builder container and source build commands. It does not download precompiled dependencies using `-i` or `-I`. Repository compatibility settings remain at their upstream defaults so official packages cannot be mistaken for Flit packages.

Bootstrap archives use the official `scripts/build-bootstraps.sh` layout, package extraction, package status records, symlink metadata, and second-stage initialization. Only the archive output path changes to `output/`, which the official builder's AppArmor policy permits writing.

Source download fallbacks retain the upstream downloader and only accept archives matching the package recipe's SHA-256. Unverified downloads never use fallback mirrors.

## Distribution

- Development packages and flat APT metadata are published to the rolling `pool` Release.
- Bootstrap archives are published under `bootstrap-flit-aarch64-<run-id>`.
- APT source: `deb [trusted=yes] https://github.com/lycstar/flit-termux-packages/releases/download/pool ./`

The APT repository uses HTTPS and explicitly trusts this distributor; it is not a signed upstream repository. The application must configure this source before installing packages. Do not install official Termux binary packages into Flit or reuse artifacts compiled for a different application prefix.

Publication uses only GitHub's job-scoped `GITHUB_TOKEN` with `contents: write`. No personal access token or external storage credentials are required. Builds run only on manual dispatch.

## Changes

Use Conventional Commits with an English imperative subject. Keep application-specific changes small and preserve the upstream build process. Device compatibility must be verified separately from successful CI compilation.
