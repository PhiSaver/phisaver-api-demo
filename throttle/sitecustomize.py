"""
Sleep THROTTLE_SLEEP_MS (default 6000) before every httpx login/token request.

Important as API is rate-limited to 10 requests per minute.
Loaded automatically by Python when this directory is on PYTHONPATH (the justfile does that).
Covers httpx.post/get, httpx.Client and phisaver-client, without touching the examples.
"""

import os
import sys
import time

try:
    import httpx

    _sleep_s = float(os.environ.get("THROTTLE_SLEEP_MS", "6000")) / 1000
    _send = httpx.Client.send

    def _throttled_send(self, request, *args, **kwargs):
        if _sleep_s > 0 and "/token/" in request.url.path:
            time.sleep(_sleep_s)
        response = _send(self, request, *args, **kwargs)
        # Rate limited: wait as long as the API asks (capped), then retry, up to 3 times
        for _ in range(3):
            if response.status_code != 429:
                break
            wait = min(float(response.headers.get("Retry-After", 5)), 60) + 1
            print(f"429 from {request.url.path}: waiting {wait:.0f}s", file=sys.stderr)
            time.sleep(wait)
            response = _send(self, request, *args, **kwargs)
        return response

    httpx.Client.send = _throttled_send
except ImportError:  # httpx not installed (e.g. system python): nothing to throttle
    pass
