"""Application logging configuration and HTTP request correlation."""

import os
import sys
from time import perf_counter
from uuid import uuid4

from loguru import logger


def configure_logging():
    logger.remove()
    logger.configure(extra={"request_id": "-"})
    logger.add(
        sys.stderr,
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format=(
            "{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {level: <8} | "
            "{extra[request_id]} | {name}:{function}:{line} | {message}"
        ),
        backtrace=False,
        diagnose=False,
    )


async def log_request(request, call_next):
    request_id = uuid4().hex
    started = perf_counter()
    with logger.contextualize(request_id=request_id):
        try:
            response = await call_next(request)
        except Exception as error:
            # Exception text can include SQL parameters, passwords or form data.
            logger.error(
                "HTTP request failed method={} error_type={} duration_ms={:.1f}",
                request.method, type(error).__name__,
                (perf_counter() - started) * 1000,
            )
            raise

        route = request.scope.get("route")
        # Log route templates rather than user-supplied paths or query strings.
        path = getattr(route, "path", "<unmatched>")
        level = "ERROR" if response.status_code >= 500 else (
            "WARNING" if response.status_code >= 400 else "INFO"
        )
        logger.log(
            level, "HTTP method={} route={} status={} duration_ms={:.1f}",
            request.method, path, response.status_code,
            (perf_counter() - started) * 1000,
        )
        response.headers["X-Request-ID"] = request_id
        return response
