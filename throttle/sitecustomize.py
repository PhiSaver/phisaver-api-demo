"""Sleep THROTTLE_SLEEP_MS (default 100) before every httpx request.

Loaded automatically by Python when this directory is on PYTHONPATH (the justfile does that).
Covers httpx.post/get, httpx.Client and phisaver-client, without touching the examples.
"""

import os
import time

try:
    import httpx

    _sleep_s = float(os.environ.get("THROTTLE_SLEEP_MS", "100")) / 1000
    _send = httpx.Client.send

    def _throttled_send(self, *args, **kwargs):
        if _sleep_s > 0:
            time.sleep(_sleep_s)
        return _send(self, *args, **kwargs)

    httpx.Client.send = _throttled_send
except ImportError:  # httpx not installed (e.g. system python): nothing to throttle
    pass
