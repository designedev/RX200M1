from waybackpy import WaybackMachineSaveAPI
import asyncio
from concurrent.futures import ProcessPoolExecutor

# Import the logger from logging_config
from conf.logging_config import logger

executor = ProcessPoolExecutor(max_workers=5)

async def archive_url(url: str) -> str:
    loop = asyncio.get_event_loop()
    try:
        save_api = WaybackMachineSaveAPI(url)
        archive_url = await loop.run_in_executor(executor, save_api.save)
        logger.info(f"Archived URL: {archive_url}")
        return archive_url
    except Exception as e:
        logger.error(f"Failed to archive URL {url}: {e}")
        return None