import asyncio
import logging

from src.PROJ.gtable.gtable_crud import g_table_main
from src.PROJ.service_pyrogram.pyro_JOBS import ScrapeVacancies


async def run_gtable():
    data = await ScrapeVacancies(test_mode=False).run()
    data = data.get("all_messages")

    await asyncio.to_thread(g_table_main, data)
    # tr1 = threading.Thread(target=g_table_main, args=(data,), name="gtable_thread").start()

    logging.warning("Saving to google sheets...")

if __name__ == "__main__":
    asyncio.run(run_gtable())
