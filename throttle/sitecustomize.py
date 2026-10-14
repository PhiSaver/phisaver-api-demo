"""
Sleep THROTTLE_SLEEP_MS (default 6000) before every httpx login/token request.

Important as API is rate-limited to 10 requests per minute.
Loaded automatically by Python when this directory is on PYTHONPATH (the justfile does that).
Covers httpx.post/get, httpx.Client and phisaver-client, without touching the examples.
"""

import os
import time

try:
    import httpx

    _sleep_s = float(os.environ.get("THROTTLE_SLEEP_MS", "6000")) / 1000
    _send = httpx.Client.send

    def _throttled_send(self, request, *args, **kwargs):
        if _sleep_s > 0 and "/token/" in request.url.path:
            time.sleep(_sleep_s)
        return _send(self, request, *args, **kwargs)

    httpx.Client.send = _throttled_send
except ImportError:  # httpx not installed (e.g. system python): nothing to throttle
    pass
