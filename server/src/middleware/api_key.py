"""API key authentication middleware.

Validates the ``X-API-Key`` header on every incoming request to ``/api/*``.
The expected key is read from the ``IPL_API_KEY`` environment variable.

When ``IPL_API_KEY`` is not set (local development), the check is skipped
so the developer experience is unaffected.
"""

import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

_API_KEY_NAME = "X-API-Key"
_api_key_header = APIKeyHeader(name=_API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(_api_key_header)) -> str | None:
    """FastAPI dependency that validates the API key.

    Returns the key on success. Raises 403 if the key is wrong.
    Skips validation entirely when ``IPL_API_KEY`` is not configured.
    """
    expected = os.getenv("IPL_API_KEY")
    if not expected:
        # No key configured — development mode, allow all requests.
        return None
    if api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid or missing API key.")
    return api_key
