from fastapi import Request
from loguru import logger
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import os

log_file_path = "logs/server.log"

log_directory = os.path.dirname(log_file_path)
if not os.path.exists(log_directory):
    try:
        os.makedirs(log_directory)
        print(f"Directory {log_directory} created")
    except Exception as e:
        print(f"Error creating directory {log_directory}: {e}")

try:
    logger.add(log_file_path, rotation="10 MB", retention="10 days", level="INFO", backtrace=True, diagnose=True)
    print(f"Logging to file {log_file_path}")
except Exception as e:
    print(f"Error adding log file {log_file_path}: {e}")


logger.add(log_file_path, rotation="10 MB", retention="7 days", level="INFO", backtrace=True, diagnose=True)


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        logger.info(f"Request: method={request.method}, url={request.url}, body={body.decode('utf-8')}")
        
        response = await call_next(request)
        if response.status_code >= 400:
            logger.error(
                f"Error Response: status={response.status_code}, method={request.method}, url={request.url}, body={body.decode('utf-8')}"
            )
        
        return response