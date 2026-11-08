"""HTTP TrustAnchor adapter for the AIRP integrity ledger."""
from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)

from .airp_ledger import TrustAnchor
from .cipher import HelixProError


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HTTPTrustAnchor(TrustAnchor):
    """Connect AIRPIntegrityLedger to an independently operated anchor.

    Bearer tokens are never placed in URLs. HTTPS is required except for
    loopback development endpoints. Redirects are refused to prevent token
    forwarding to another origin.
    """

    def __init__(self, base_url: str, bearer_token: str, *, timeout: float = 5.0):
        base_url = base_url.rstrip("/")
        parsed = urlsplit(base_url)
        loopback_hosts = {"127.0.0.1", "localhost", "::1"}
        if (
            parsed.scheme != "https" and not (parsed.scheme == "http" and parsed.hostname in loopback_hosts)
        ) or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise HelixProError("TrustAnchor requires HTTPS except on loopback and rejects URL credentials/query/fragment")
        if not bearer_token or len(bearer_token) < 32:
            raise HelixProError("TrustAnchor bearer token must contain at least 32 characters")
        if timeout <= 0 or timeout > 60:
            raise HelixProError("TrustAnchor timeout must be in (0, 60] seconds")
        self.base_url = base_url
        self._token = bearer_token
        self.timeout = timeout
        self._opener = build_opener(_NoRedirect)

    def _request(self, method: str, path: str, body: bytes | None = None):
        headers = {"Authorization": "Bearer " + self._token, "Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        request = Request(self.base_url + path, data=body, headers=headers, method=method)
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                return response.status, response.read(8193)
        except HTTPError as exc:
            return exc.code, exc.read(8193)
        except (URLError, TimeoutError, OSError) as exc:
            raise HelixProError(f"AIRP TrustAnchor connection failed: {type(exc).__name__}") from exc

    def publish_checkpoint(self, checkpoint: bytes) -> None:
        status, body = self._request("POST", "/v1/checkpoints", checkpoint)
        if status != 200:
            try:
                detail = json.loads(body.decode("utf-8")).get("detail", "request rejected")
            except Exception:
                detail = "request rejected"
            raise HelixProError(f"AIRP TrustAnchor rejected checkpoint (HTTP {status}): {detail}")

    def latest_checkpoint(self) -> bytes | None:
        status, body = self._request("GET", "/v1/checkpoints/latest")
        if status == 404:
            return None
        if status != 200:
            raise HelixProError(f"AIRP TrustAnchor latest checkpoint failed (HTTP {status})")
        if len(body) > 8192:
            raise HelixProError("AIRP TrustAnchor returned an oversized checkpoint")
        return body
