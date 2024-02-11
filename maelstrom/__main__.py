import asyncio
from aioshutdown import SIGTERM, SIGINT, SIGHUP
from .main import main


if __name__ == "__main__":
    with SIGTERM | SIGHUP | SIGINT as loop:
        task = loop.create_task(main())
        loop.run_until_complete(asyncio.gather(task))
