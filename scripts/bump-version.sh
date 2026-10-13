#!/usr/bin/env bash
# DaVinci Writer — Bump Version
# Updates every hardcoded version reference across the repo so a release can
# be cut with a single source of truth for the version number.
#
# Usage:
#   ./scripts/bump-version.sh 1.0.1      (X.Y or X.Y.Z)

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

VER_RE='[0-9]+\.[0-9]+(\.[0-9]+)?'

NEW_VERSION="${1:-}"
if [[ -z "$NEW_VERSION" ]]; then
    echo "[ERROR] Usage: ./scripts/bump-version.sh <new_version>  (e.g. 1.0.1)" >&2
    exit 1
fi
if ! [[ "$NEW_VERSION" =~ ^${VER_RE}$ ]]; then
    echo "[ERROR] Version must look like X.Y or X.Y.Z (e.g. 1.0.1)." >&2
    exit 1
fi

OLD_VERSION=$(grep -m1 -oE "VERSION = \"${VER_RE}\"" web/app.py | grep -oE "${VER_RE}")
if [[ -z "$OLD_VERSION" ]]; then
    echo "[ERROR] Could not detect current version in web/app.py." >&2
    exit 1
fi
if [[ "$OLD_VERSION" == "$NEW_VERSION" ]]; then
    echo "[ERROR] New version ($NEW_VERSION) matches current version. Nothing to do." >&2
    exit 1
fi

MONTH_YEAR=$(date '+%B %Y')
OLD_RE="${OLD_VERSION//./\\.}"

# Portable in-place edit (GNU and BSD sed differ on -i), using extended regex.
sed_inplace() {
    sed -E "$1" "$2" > "$2.tmp" && mv "$2.tmp" "$2"
}

echo "[..] Bumping version: $OLD_VERSION -> $NEW_VERSION"

sed_inplace "s/VERSION = \"${OLD_RE}\"/VERSION = \"${NEW_VERSION}\"/" web/app.py
sed_inplace "s/RELEASE_DATE = \"[A-Za-z]+ [0-9]{4}\"/RELEASE_DATE = \"${MONTH_YEAR}\"/" web/app.py

for f in README.md docs/QUICKSTART.md docs/USER-MANUAL.md; do
    sed_inplace "s/DaVinci-v${OLD_RE}\.zip/DaVinci-v${NEW_VERSION}.zip/g" "$f"
done

for f in README.md docs/ABOUT.md docs/USER-MANUAL.md; do
    sed_inplace "s/version = \{${OLD_RE}\}/version = {${NEW_VERSION}}/" "$f"
    sed_inplace "s/v${OLD_RE}, 20[0-9]{2}/v${NEW_VERSION}, 2026/" "$f"
done

sed_inplace "s/^  v${OLD_RE} · /  v${NEW_VERSION} · /" README.md
sed_inplace "s/\*\*Version ${OLD_RE}\*\* · [A-Za-z]+ [0-9]{4}/**Version ${NEW_VERSION}** · ${MONTH_YEAR}/" docs/ABOUT.md
sed_inplace "s/\*\*Version:\*\* ${OLD_RE} · \*\*Last Updated:\*\* [A-Za-z]+ [0-9]{4}/**Version:** ${NEW_VERSION} · **Last Updated:** ${MONTH_YEAR}/" docs/USER-MANUAL.md

# Release helper defaults and examples (match any X.Y[.Z] so stale values are refreshed too)
sed_inplace "s/(\\\$Version = \")${VER_RE}(\")/\1${NEW_VERSION}\3/" scripts/windows/create-release.ps1
sed_inplace "s/(make-release\.ps1 -Version )${VER_RE}/\1${NEW_VERSION}/; s/(\(e\.g\. )${VER_RE}(\))/\1${NEW_VERSION}\3/" scripts/windows/make-release.ps1
sed_inplace "s/DaVinci-v${VER_RE}\.zip/DaVinci-v${NEW_VERSION}.zip/" test-release-contents.ps1

echo "[..] Updated files:"
git diff --stat

echo ""
echo "Next steps:"
echo "  Add a v${NEW_VERSION} entry to CHANGELOG.md, then:"
echo "  git add -A"
echo "  git commit -m \"Release v${NEW_VERSION}\""
echo "  git tag v${NEW_VERSION}"
echo "  git push origin main --tags   # triggers .github/workflows/release.yml"
