"""Compression middleware for API responses."""

from starlette.middleware.gzip import GZipMiddleware as StarletteGZipMiddleware


class CompressionMiddleware(StarletteGZipMiddleware):
    """
    Gzip compression middleware for API responses.

    Automatically compresses responses larger than minimum_size bytes
    when client supports gzip encoding.
    """

    def __init__(self, app, minimum_size: int = 500) -> None:
        """
        Initialize compression middleware.

        Args:
            app: ASGI application
            minimum_size: Minimum response size in bytes to compress (default: 500)
        """
        super().__init__(app, minimum_size=minimum_size)
