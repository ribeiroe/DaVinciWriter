#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/../.."

REQ_FILE="web/requirements.txt"
REQ_HASH_FILE=".venv/.requirements.sha256"

echo ""
echo "========================================"
echo "  DaVinci Writer - Starting"
echo "========================================"
echo ""

# Step 1: Check Python
echo "[1/6] Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found. Please install Python 3.10+"
    read -p "Press Enter to exit..."
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "[1/6] Python $PYTHON_VERSION found ✓"
echo ""

# Step 2: Check virtual environment
echo "[2/6] Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "[2/6] Virtual environment exists ✓"
else
    echo "[2/6] Creating virtual environment..."
    python3 -m venv .venv
    echo "[2/6] Virtual environment created ✓"
fi
echo ""

# Step 3: Activate and install dependencies only when needed
echo "[3/6] Checking dependencies..."
source .venv/bin/activate
CURRENT_REQ_HASH=""
if command -v shasum >/dev/null 2>&1; then
    CURRENT_REQ_HASH="$(shasum -a 256 "$REQ_FILE" | awk '{print $1}')"
fi

STORED_REQ_HASH=""
if [ -f "$REQ_HASH_FILE" ]; then
    STORED_REQ_HASH="$(cat "$REQ_HASH_FILE" 2>/dev/null || true)"
fi

if [ -z "$CURRENT_REQ_HASH" ] || [ "$CURRENT_REQ_HASH" != "$STORED_REQ_HASH" ]; then
    echo "[3/6] Installing/updating dependencies..."
    python3 -m pip install --upgrade pip -q
    python3 -m pip install -r "$REQ_FILE" -q
    if [ -n "$CURRENT_REQ_HASH" ]; then
        printf "%s\n" "$CURRENT_REQ_HASH" > "$REQ_HASH_FILE"
    fi
    echo "[3/6] Dependencies installed ✓"
else
    echo "[3/6] Dependencies already up to date ✓"
fi
echo ""

# Step 4: Check .env file
echo "[4/6] Checking configuration..."
if [ -f ".env" ]; then
    echo "[4/6] Configuration file found ✓"
else
    echo "[4/6] WARNING: .env file not found. Using defaults."
fi
echo ""

# Step 5: Kill existing process on port 8501
echo "[5/6] Clearing port 8501..."
if command -v lsof &> /dev/null; then
    PIDS="$(lsof -ti tcp:8501 | tr '\n' ' ' || true)"
    if [ -n "${PIDS// }" ]; then
        kill $PIDS >/dev/null 2>&1 || true
        sleep 1
    fi
fi
echo "[5/6] Port ready ✓"
echo ""

# Step 6: Start application
echo "[6/6] Starting application..."
echo "========================================"
echo "  Opening application on http://localhost:8501"
echo "========================================"
echo ""

# Open browser in background
if command -v open >/dev/null 2>&1; then
    ( sleep 3; open "http://localhost:8501" ) &
fi

# Start streamlit (headless + no usage-stats prompt so it doesn't block waiting for input)
exec streamlit run web/app.py --server.headless true --browser.gatherUsageStats false
