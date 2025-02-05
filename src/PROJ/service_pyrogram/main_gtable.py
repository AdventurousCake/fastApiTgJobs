import asyncio
import logging
import threading

from src.PROJ.service_pyrogram.gtable_crud import g_table_main
from src.PROJ.service_pyrogram.pyro_JOBS import ScrapeVacancies


async def main():
    data = await ScrapeVacancies(test_mode=False).run()
    data = data.get("all_messages")

    tr1 = threading.Thread(target=g_table_main, args=(data,), name="gtable_thread")
    tr1.start()
    logging.warning("Saving to google sheets...")

if __name__ == "__main__":
    asyncio.run(main())
