#!/usr/bin/env bash
set -euo pipefail
: "${GH_REPO:?GH_REPO is required}"
: "${GH_TOKEN:?GH_TOKEN is required}"
: "${GITHUB_SHA:?GITHUB_SHA is required}"
[[ $# == 1 && -d "$1" ]] || exit 64
new_packages="$(realpath "$1")"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

if gh release view pool --repo "$GH_REPO" >/dev/null 2>&1; then
	# A download failure must stop publication, otherwise an incomplete index
	# could silently remove packages from the existing repository.
	gh release download pool --repo "$GH_REPO" --pattern '*.deb' --dir "$work"
else
	gh release create pool --repo "$GH_REPO" --target "$GITHUB_SHA" \
		--title 'Flit APT packages (aarch64)' --notes 'Rolling package repository for cc.lycstar.flit.'
fi
find "$new_packages" -type f -name '*.deb' -exec cp {} "$work/" \;
for file in "$work"/*.deb; do
	[[ -f "$file" ]] || { echo 'No packages to publish' >&2; exit 1; }
	# GitHub normalizes colons in asset filenames. Use the same names in APT.
	name="$(basename "$file")"
	if [[ "$name" == *:* ]]; then mv "$file" "$work/${name//:/.}"; fi
done
python3 "$(dirname "$0")/generate-index.py" "$work"
# Publish packages before metadata so every indexed package is downloadable.
find "$work" -maxdepth 1 -name '*.deb' -print0 |
	xargs -0 -n 30 gh release upload pool --repo "$GH_REPO" --clobber
gh release upload pool --repo "$GH_REPO" --clobber \
	"$work/Packages" "$work/Packages.gz" "$work/Packages.xz" "$work/Release"
echo "APT source: deb [trusted=yes] https://github.com/$GH_REPO/releases/download/pool ./"
