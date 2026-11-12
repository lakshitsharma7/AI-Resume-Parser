import time
import json
import logging
from typing import Optional, Dict, Any, Tuple
import httpx

from app.config import settings
from app.services.ssrf_validator import validate_destination_url

logger = logging.getLogger(__name__)

class DestinationForwarder:
    """
    Safely sends parsed resume JSON to external destination APIs with SSRF protection,
    authentication header injection, timeout protection, and token masking.
    """

    @classmethod
    async def forward_json(
        cls,
        payload: Dict[str, Any],
        destination_url: str,
        auth_token: Optional[str] = None,
        auth_header_name: str = "Authorization",
        auth_scheme: Optional[str] = "Bearer",
        custom_headers_json: Optional[str] = None
    ) -> Tuple[bool, int, Any, float, Optional[str]]:
        """
        Sends payload to destination_url.
        
        Returns:
            (success_bool, status_code, response_data, duration_ms, masked_auth_header)
        """
        # 1. SSRF Validation
        is_valid, error_msg = validate_destination_url(
            destination_url,
            allow_local=settings.ALLOW_LOCAL_DESTINATIONS
        )
        if not is_valid:
            logger.warning(f"SSRF block triggered for destination: {destination_url} - {error_msg}")
            return False, 403, {"error": "SSRF_PROTECTION_BLOCKED", "detail": error_msg}, 0.0, None

        # 2. Build Headers safely
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AI-Resume-Parser-Forwarder/1.0"
        }

        masked_auth = None
        if auth_token:
            clean_token = auth_token.strip()
            if auth_scheme and auth_scheme.strip():
                header_val = f"{auth_scheme.strip()} {clean_token}"
                masked_auth = f"{auth_scheme.strip()} ****"
            else:
                header_val = clean_token
                masked_auth = "****"
            headers[auth_header_name.strip()] = header_val

        # Add custom headers if provided
        if custom_headers_json:
            try:
                extra = json.loads(custom_headers_json)
                if isinstance(extra, dict):
                    for k, v in extra.items():
                        headers[str(k)] = str(v)
            except Exception as e:
                logger.warning(f"Failed to parse custom headers JSON: {e}")

        # 3. Execute HTTP POST Request with timeout
        start_time = time.time()
        timeout = httpx.Timeout(settings.FORWARD_REQUEST_TIMEOUT, connect=5.0)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                res = await client.post(destination_url, json=payload, headers=headers)
                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                # Attempt JSON response decoding, fallback to raw text
                try:
                    res_body = res.json()
                except Exception:
                    res_body = res.text[:2000]

                success = 200 <= res.status_code < 300
                return success, res.status_code, res_body, elapsed_ms, masked_auth

        except httpx.TimeoutException:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Destination request timed out after {settings.FORWARD_REQUEST_TIMEOUT}s: {destination_url}")
            return False, 504, {
                "error": "GATEWAY_TIMEOUT",
                "detail": f"Destination API did not respond within {settings.FORWARD_REQUEST_TIMEOUT} seconds."
            }, elapsed_ms, masked_auth

        except httpx.RequestError as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(f"Failed to connect to destination API: {str(e)}")
            return False, 502, {
                "error": "BAD_GATEWAY",
                "detail": f"Failed to reach destination API: {type(e).__name__}"
            }, elapsed_ms, masked_auth

        except Exception as e:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            logger.exception("Unexpected error during destination forwarding")
            return False, 500, {
                "error": "INTERNAL_FORWARDING_ERROR",
                "detail": str(e)
            }, elapsed_ms, masked_auth

