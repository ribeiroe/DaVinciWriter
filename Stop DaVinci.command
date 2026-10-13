#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

TARGET="scripts/macos/stop-webui.command"

if [ ! -f "$TARGET" ]; then
  echo "Could not find $TARGET"
  exit 1
fi

exec "$TARGET"
