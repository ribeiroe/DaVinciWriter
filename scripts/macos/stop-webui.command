#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/../.."

echo ""
echo "========================================"
echo "  DaVinci Writer - Stopping"
echo "========================================"
echo ""

get_port_pids() {
    lsof -ti tcp:8501 | tr '\n' ' ' || true
}

# Step 1: Check if app is running
echo "[1/3] Checking if application is running..."
if command -v lsof &> /dev/null; then
    PIDS="$(get_port_pids)"
    if [ -z "${PIDS// }" ]; then
        echo "[1/3] Application is not running ✓"
        echo ""
        echo "========================================"
        echo "  Already stopped"
        echo "========================================"
        echo ""
        read -p "Press Enter to exit..."
        exit 0
    fi
    echo "[1/3] Application found running on port 8501 ✓"
else
    echo "[1/3] WARNING: lsof command not found"
fi
echo ""

# Step 2: Stop application
echo "[2/3] Stopping application..."
if command -v lsof &> /dev/null; then
    PIDS="$(get_port_pids)"
    if [ -n "${PIDS// }" ]; then
        kill $PIDS >/dev/null 2>&1 || true
    fi
fi
echo "[2/3] Stop signal sent ✓"
echo ""

# Step 3: Verify it stopped
echo "[3/3] Verifying application stopped..."
if command -v lsof &> /dev/null; then
    STOPPED=0
    for _ in $(seq 1 8); do
        PIDS="$(get_port_pids)"
        if [ -z "${PIDS// }" ]; then
            STOPPED=1
            break
        fi
        sleep 0.25
    done

    if [ "$STOPPED" -eq 0 ] && [ -n "${PIDS// }" ]; then
        echo "[3/3] Process still running, forcing stop..."
        kill -9 $PIDS >/dev/null 2>&1 || true
        sleep 0.5
        PIDS="$(get_port_pids)"
    fi

    if [ -z "${PIDS// }" ]; then
        echo "[3/3] Port 8501 is now free ✓"
        echo ""
        echo "========================================"
        echo "  Application stopped successfully!"
        echo "========================================"
        echo ""
    else
        echo "[3/3] WARNING: Port still in use"
        echo ""
        echo "========================================"
        echo "  Attempted to stop but port may still be in use"
        echo "========================================"
        echo ""
    fi
fi

read -p "Press Enter to exit..."
