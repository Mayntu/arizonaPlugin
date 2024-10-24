from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from src.configs.logs_config import setup_logging
import json
import logging

setup_logging()

logger = logging.getLogger("__main__")
separator_logger = logging.getLogger("separator_logger")

LOGS_SEPARATOR_OK: str = "-----------------------------------------REQUEST INFO-----------------------------------------"
LOGS_SEPARATOR_ER: str = "-----------------------------------------REQUEST ERROR-----------------------------------------"

class LogsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            request_body = await request.json()
        except Exception:
            request_body = None

        response = await call_next(request)

        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk

        if response.status_code >= 400:
            separator_logger.info(LOGS_SEPARATOR_ER)
            logger.error(f"{request.method} '{request.url.path}'")
            logger.error(f"Error | {response.status_code}")
            if request_body:
                logger.error(f"Request body  | {json.dumps(request_body)}")
            logger.error(f"Response body | {response_body.decode('utf-8') if response_body else 'No response body'}")
        else:
            separator_logger.info(LOGS_SEPARATOR_OK)
            logger.info(f"{request.method} '{request.url.path}'")
            logger.info(f"Response status {response.status_code}")

        response.body_iterator = iter([response_body])
        response.body_iterator = self._iter_response_body(response_body)
        return response

    async def _iter_response_body(self, body: bytes):
        yield body
