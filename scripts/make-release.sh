#!/usr/bin/env bash
# DaVinci Writer — Build Release Zip
# Produces a self-contained folder that anyone can unzip and launch with
# a double-click on "Start DaVinci.command" (macOS) or scripts\windows\setup.bat.
#
# Usage:
#   ./scripts/make-release.sh          # interactive (prompts for version)
#   ./scripts/make-release.sh 1.2      # non-interactive (CI) — overwrites existing zip
set -euo pipefail

# Always run from repo root
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

echo ""
echo "============================================"
echo "  DaVinci Writer — Build Release Zip"
echo "============================================"
echo ""

# ── Version (argument, or prompt when run interactively) ─────────────────────
VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
    read -rp "  Version number (e.g. 1.1): " VERSION
fi
if [[ -z "$VERSION" ]]; then
    echo "[ERROR] Version cannot be empty." >&2
    exit 1
fi

ZIP_NAME="DaVinci-v${VERSION}.zip"
FOLDER_NAME="DaVinci-v${VERSION}"
TMP="/tmp/${FOLDER_NAME}"

if [[ -f "$ZIP_NAME" ]]; then
    if [[ -n "${1:-}" ]]; then
        rm "$ZIP_NAME"   # non-interactive: overwrite
    else
        read -rp "  $ZIP_NAME already exists. Overwrite? [y/N]: " OVERWRITE
        if [[ "$OVERWRITE" != "y" && "$OVERWRITE" != "Y" ]]; then exit 0; fi
        rm "$ZIP_NAME"
    fi
fi

# ── Stage into temp folder ────────────────────────────────────────────────────
echo "[..] Staging files..."
rm -rf "$TMP"
mkdir -p "$TMP"

rsync -a \
    --exclude='.git' \
    --exclude='.venv' \
    --exclude='output/*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='.davinci.log' \
    --exclude='.davinci.pid' \
    --exclude='DaVinci-v*.zip' \
    --exclude='web/.sessions' \
    --exclude='.DS_Store' \
    . "$TMP/"

# Strip personal source files; keep only README.md placeholders
for DIR in theses artefacts papers my-papers my-response-letters submitted-papers reviewer-feedback; do
    P="$TMP/sources/$DIR"
    if [[ -d "$P" ]]; then
        find "$P" -mindepth 1 ! -name 'README.md' -delete
    fi
done

# Create required output dirs so the app starts cleanly
mkdir -p "$TMP/output/knowledge/sources"

# Keep launchers from the repository as-is so release zips include latest fixes.
chmod +x \
    "$TMP/Start DaVinci.command" \
    "$TMP/Stop DaVinci.command" \
    "$TMP/scripts/macos/run-webui.command" \
    "$TMP/scripts/macos/stop-webui.command"

# ── Pack zip ──────────────────────────────────────────────────────────────────
echo "[..] Creating $ZIP_NAME..."

(cd /tmp && zip -r "$REPO_DIR/$ZIP_NAME" "$FOLDER_NAME" \
    -x "*.DS_Store" \
    -x "*/__pycache__/*" \
    -x "*.pyc")

rm -rf "$TMP"

SIZE=$(du -sh "$REPO_DIR/$ZIP_NAME" | cut -f1)

echo ""
echo "============================================"
echo "  Release built successfully!"
echo "============================================"
echo ""
echo "  File : $ZIP_NAME"
echo "  Size : $SIZE"
echo ""
echo "  How to distribute:"
echo "    1. Share $ZIP_NAME"
echo "    2. Recipient unzips the file"
echo "    3. Double-click  'Start DaVinci.command'  to launch"
echo "    4. Double-click  'Stop DaVinci.command'   to stop"
echo ""
