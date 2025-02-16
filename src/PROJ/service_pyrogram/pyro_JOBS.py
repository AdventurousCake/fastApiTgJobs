import asyncio
import itertools
import logging
from typing import List

from pyrogram import Client

from src.PROJ.api.schemas_jobs import VacancyData
from src.PROJ.core.config import TG_SESSION_STRING, MSG_LIMIT, MSG_MIN_DATE, PASS_SENIORS_TMP, \
    TASK_EXECUTION_TIME_LIMIT, UNIQUE_FILTER, TARGET_CHATS, TARGET_CHATS_TEST, IMG_SAVE
from src.PROJ.core.utils import ImageUploader
from src.PROJ.service_pyrogram.pyro_msg_parser import MessageParser

# logging.basicConfig(
#     level="INFO",
#     format="%(message)s",
#     datefmt="[%X]",
#     handlers=[RichHandler(rich_tracebacks=True, console=console)],)
# logger = logging.getLogger("rich")

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, session_name: str = None, api_id: int = None, api_hash: str = None, phone_number: str = None,
                 password: str = None, session_string: str = None):
        if not session_name:
            logger.warning("Starting in memory session client")
            self.client = Client(":memory:", session_string=session_string)
        else:
            self.client = Client(session_name, api_id, api_hash, phone_number=phone_number, password=password)

    async def __aenter__(self):
        await self.client.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.stop()

    @staticmethod
    async def progress(current, total):
        print(f"{current * 100 / total:.1f}%")

    async def file_id_to_bytes(self, file_id):
        file = await self.client.download_media(file_id, in_memory=True, block=True)
        file_bytes = bytes(file.getbuffer())
        file_name = file.name
        return file_bytes

    # parsed
    async def get_chat_data(self, chat_id: int, msg_limit: int) -> List[VacancyData]:
        chat_data = await self.client.get_chat(chat_id)
        logger.info(f"""Processing chat: {chat_data.title} - @{chat_data.username}""")

        messages: List[VacancyData] = []
        messages_set_text_255 = []  # for check unique

        async for message in self.client.get_chat_history(chat_id, limit=msg_limit):
            # pre filter + unique
            if message.date < MSG_MIN_DATE:
                continue

            parsed_message = await MessageParser().parse_message(message, chat_data.username)
            if parsed_message:
                # check unique
                if UNIQUE_FILTER:
                    if parsed_message.text_[:255] in messages_set_text_255:
                        continue
                    messages_set_text_255.append(parsed_message.text_[:255])

                messages.append(parsed_message)
        return messages


class ScrapeVacancies:
    def __init__(self, target_chats=None, test_mode=False):
        if target_chats is None and not test_mode:
            target_chats = TARGET_CHATS

        elif test_mode:
            target_chats = TARGET_CHATS_TEST
        self.target_chats = target_chats

    # @classmethod
    async def run(self) -> dict:
        """to get ids use forward to bot https://t.me/ShowJsonBot"""

        logger.warning(
            f"""Starting job search.
            USING ENV KEY TG SESSION
            TASK_EXECUTION_TIME_LIMIT: {TASK_EXECUTION_TIME_LIMIT}s;
            { MSG_LIMIT=};
            MSG MIN DATE: {MSG_MIN_DATE.strftime('%Y-%m-%d')}
            { UNIQUE_FILTER=}
            { IMG_SAVE=}
            ======================================
            PASS seniors (temporary): {PASS_SENIORS_TMP}
            Target chats ({len(self.target_chats)}): {self.target_chats}
            ======================================"""
        )

        async with TelegramClient(session_string=TG_SESSION_STRING) as client:
            c_data = await client.client.get_me()
            logger.warning(f"Bot id: {c_data.id}; Name: {c_data.first_name}")

            # list of coroutines
            tasks = [asyncio.wait_for(client.get_chat_data(chat_id, MSG_LIMIT),
                                      timeout=TASK_EXECUTION_TIME_LIMIT)
                     for chat_id in self.target_chats]

            # await выполнения функций, return:list of results [[VacancyData, ...]]
            chat_results: List[List[VacancyData] | Exception] = await asyncio.gather(*tasks, return_exceptions=True)

            chat_results_flat = list(itertools.chain(*chat_results))

            if IMG_SAVE:
                images_ids = set([message.user_image_id for message in chat_results_flat])
                photos_ = await ImageUploader().upload(images_ids, client)

        # not separated by chats
        all_messages_new: List[VacancyData] = []
        hrs = {}
        errors = []

        for idx, result in enumerate(chat_results):
            logger.info(f"Chat {self.target_chats[idx]}: {len(result)}")

            if isinstance(result, Exception):
                if isinstance(result, asyncio.CancelledError):
                    logger.error(f"asyncio.CancelledError in TASK get_chat_data", exc_info=result)
                elif isinstance(result, asyncio.TimeoutError):
                    logger.error(f"asyncio.TimeoutError in TASK get_chat_data", exc_info=result)
                else:
                    logger.error(f"Error in get_chat_data", exc_info=result)
                errors.append(result)

            # good result
            else:
                for message in result:
                    # check if channel
                    user_tg_id = message.user_tg_id
                    if not user_tg_id:
                        user_tg_id = message.chat_id

                    hrs.update({user_tg_id: message.user_username})

                    if IMG_SAVE:
                        message.user_image_url = photos_.get(message.user_image_id)

                    all_messages_new.append(message)  # message.model_dump()

        # unique by url
        unique_count = len(set([m.msg_url for m in all_messages_new]))
        logger.warning(f'[red] Found {len(all_messages_new)}, unique msgs: {unique_count};\n'
                       f'Unique HRs {len(hrs)}. Errors: {len(errors)}[/]')
        # post proc
        all_messages_new.sort(key=lambda x: x.posted_at, reverse=True)
        hr_data = tuple(hrs.items())

        return dict(all_messages=all_messages_new, hr_data=hr_data)


if __name__ == "__main__":
    # start_time = asyncio.get_event_loop().time()
    # end_time = asyncio.get_event_loop().time()
    # logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")

    asyncio.run(ScrapeVacancies(test_mode=True).run())
