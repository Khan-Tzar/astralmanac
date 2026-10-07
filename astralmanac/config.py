# astralmanac/config.py
"""Runtime configuration, read from environment variables.

Astralmanac is designed to run with zero configuration: every data source in
the default set is key-free, so ``docker compose up`` works out of the box. A
source that needs a key (e.g. NASA's own APIs) simply stays dormant until its
key is provided.
"""
import os

# Where the SQLite store lives. In Docker this is a mounted volume.
DB_PATH = os.environ.get("ASTRALMANAC_DB", os.path.join(os.getcwd(), "data", "astralmanac.db"))

# How often the scheduler re-runs each fetcher, in seconds. Space data changes
# slowly; the default is deliberately gentle on the upstream APIs.
FETCH_INTERVAL_SECONDS = int(os.environ.get("ASTRALMANAC_FETCH_INTERVAL", str(6 * 3600)))

# Network timeout for a single upstream request.
REQUEST_TIMEOUT_SECONDS = int(os.environ.get("ASTRALMANAC_HTTP_TIMEOUT", "30"))

# A contact string sent as the User-Agent, so upstream operators can identify
# the traffic. Override it with your own deployment's URL or email.
USER_AGENT = os.environ.get(
    "ASTRALMANAC_USER_AGENT",
    "astralmanac/0.1 (+https://github.com/your-org/astralmanac)",
)

# Optional NASA api.nasa.gov key. Unset -> NASA-keyed sources stay dormant.
NASA_API_KEY = os.environ.get("NASA_API_KEY", "")

# Web server bind.
HOST = os.environ.get("ASTRALMANAC_HOST", "0.0.0.0")
PORT = int(os.environ.get("ASTRALMANAC_PORT", "8000"))
