# alpha v0.0.1

import uvicorn
import asyncio
from src.init import create_app

async def main():
    app = await create_app()
    config = uvicorn.Config(app, host="0.0.0.0", port=5000, workers=3, timeout_graceful_shutdown=10)
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
