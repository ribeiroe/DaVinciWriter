# ── Build stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

WORKDIR /app

# Install dependencies first (cached layer)
COPY web/requirements.txt ./web/requirements.txt
RUN pip install --no-cache-dir -r web/requirements.txt

# ── Application ───────────────────────────────────────────────────────────────
# Copy app code
COPY web/ ./web/

# Copy pre-configured venue data (read-only reference data)
COPY sources/venues/ ./sources/venues/

# Copy agent definitions and docs
COPY .github/ ./.github/
COPY docs/     ./docs/
COPY AGENTS.md README.md ./

# Create user-data directories (will be overridden by volume mounts at runtime)
RUN mkdir -p \
    sources/theses \
    sources/artefacts \
    sources/papers \
    sources/my-papers \
    sources/reviewer-feedback \
    sources/my-response-letters \
    sources/submitted-papers \
    output/knowledge/sources

# Streamlit config: disable telemetry, run headless
RUN mkdir -p /root/.streamlit && printf \
    '[server]\nheadless = true\naddress = "0.0.0.0"\nport = 8501\n\n[browser]\ngatherUsageStats = false\n' \
    > /root/.streamlit/config.toml

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')" || exit 1

ENTRYPOINT ["python", "-m", "streamlit", "run", "web/app.py"]
