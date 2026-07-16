"""Request logging and suspicious-activity detection middleware.

Logs every request with: timestamp, client IP, method, path, status code,
and response time in milliseconds.

Flags any IP that accumulates 3+ rate-limited (429) or forbidden (403)
responses with a WARNING-level log entry.
"""

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("ipl.security")

# In-memory counter: IP -> count of suspicious responses (429/403).
# Reset on server restart, which is acceptable for basic detection.
_suspicious_counts: dict[str, int] = defaultdict(int)

_SUSPICIOUS_THRESHOLD = 3


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs every request and flags potentially abusive clients."""

    async def dispatch(self, request: Request, call_next) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        start = time.perf_counter()

        response = await call_next(request)

        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        status = response.status_code

        logger.info(
            "%s %s %s -> %s (%.1fms)",
            client_ip,
            request.method,
            request.url.path,
            status,
            elapsed_ms,
        )

        # Track suspicious responses
        if status in (429, 403):
            _suspicious_counts[client_ip] += 1
            if _suspicious_counts[client_ip] >= _SUSPICIOUS_THRESHOLD:
                logger.warning(
                    "SUSPICIOUS: IP %s has received %d blocked responses (429/403)",
                    client_ip,
                    _suspicious_counts[client_ip],
                )

        return response
