import logging
import time
from uuid import uuid4

from fastapi import Request


logger = logging.getLogger("uvicorn.error")


async def request_logging_middleware(
    request: Request,
    call_next
):
    request_id = uuid4().hex
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "Request failed | id=%s | method=%s | "
            "path=%s | duration=%.2fms",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed | id=%s | method=%s | "
        "path=%s | status=%s | duration=%.2fms",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response