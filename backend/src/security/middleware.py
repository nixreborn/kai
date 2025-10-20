"""Security middleware for Kai backend."""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all HTTP responses.

    This middleware adds the following security headers:
    - X-Content-Type-Options: Prevents MIME sniffing
    - X-Frame-Options: Prevents clickjacking
    - X-XSS-Protection: Enables XSS filter
    - Referrer-Policy: Controls referrer information
    - Permissions-Policy: Controls browser features
    - Content-Security-Policy: Restricts resource loading
    - Strict-Transport-Security: Forces HTTPS (production only)
    """

    async def dispatch(self, request: Request, call_next: callable) -> Response:
        """
        Process request and add security headers to response.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain

        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS filter in browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Restrict browser features
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        # Content Security Policy
        if getattr(settings, "csp_enabled", True):
            csp_directives = [
                "default-src 'self'",
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data: https:",
                "font-src 'self' data:",
                "connect-src 'self'",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
            ]
            response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # HSTS (HTTP Strict Transport Security) for production
        if not settings.debug and getattr(settings, "ssl_enabled", False):
            hsts_max_age = getattr(settings, "hsts_max_age", 31536000)
            hsts_value = f"max-age={hsts_max_age}"
            if getattr(settings, "hsts_include_subdomains", True):
                hsts_value += "; includeSubDomains"
            response.headers["Strict-Transport-Security"] = hsts_value

        return response
