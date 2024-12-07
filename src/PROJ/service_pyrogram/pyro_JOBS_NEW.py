import asyncio
import csv
import itertools
import logging
import re
from datetime import datetime, timedelta, UTC
from pprint import pprint
from typing import Optional, List

import httpx
from aiohttp import ClientSession, FormData
from pydantic import ValidationError
from pyrogram import Client
from pyrogram.types import Message

from src.PROJ.api.schemas_jobs import VacancyData
from src.PROJ.core.config import TG_SESSION_STRING

# logging.basicConfig(
#     level="INFO",
#     format="%(message)s",
#     datefmt="[%X]",
#     handlers=[RichHandler(rich_tracebacks=True, console=console)],
# )
# logger = logging.getLogger("rich")


logger = logging.getLogger(__name__)

MSG_LIMIT = 500
MSG_MIN_DATE = datetime.utcnow() - timedelta(days=31)  # datetime.now(UTC)
SESSION_NAME = "my_account_MEGAFON"
PASS_SENIORS_TMP = True
TASK_EXECUTION_TIME_LIMIT = 60 * 5
UNIQUE_FILTER=True


class MsgFilter:
    @staticmethod
    def is_ads_and_img(message):
        """нет текста и есть подпись"""
        if not message.text and message.caption:
            return True
        else:
            return False

    @staticmethod
    def is_empty(message):
        return True if not message.text else False


class VacancyFilter:
    VACANCY_PATTERN = re.compile(r"vacancy|#вакансия", re.IGNORECASE)
    # bool(VACANCY_PATTERN.search(text))

    # TUPLES ONLY
    SENIOR_KEYS = ("#lead", "senior", "#teamlead ",
                   "team lead", "#techlead", "#qa")
    SENIOR_KEYS_EXCLUDE = ("middle", "junior")
    REMOTE_KEYS = ("#удаленка", "#remote", "#удаленно")
    STARTUP_KEYS = ("стартап",)
    BIGTECH_RU_KEYS = ("yandex", "sber", 'яндекс',
                       'сбер', 'team.vk', 'kaspersky')

    ONLY_VACANCIES_CHANNELS = ("job_python", "python_djangojobs", "p_rabota")
    OFFICE_KEYS = ("#офис",)

    @staticmethod
    def is_simple_filter(text, keys) -> bool:
        return any(key in text for key in keys)

    @staticmethod
    def is_bigtech(text):
        return VacancyFilter.is_simple_filter(text, VacancyFilter.BIGTECH_RU_KEYS)

    @staticmethod
    def is_vacancy(text: str, chat_username: str) -> bool:
        return bool(
            VacancyFilter.VACANCY_PATTERN.search(text)
            or chat_username in VacancyFilter.ONLY_VACANCIES_CHANNELS
        )

    @staticmethod
    def is_senior_position(text):
        if (any(key in text
                for key in VacancyFilter.SENIOR_KEYS)

                and not any(key in text
                            for key in VacancyFilter.SENIOR_KEYS_EXCLUDE)):
            return True

    @staticmethod
    def is_remote(text):
        return any(key in text for key in VacancyFilter.REMOTE_KEYS)

    @staticmethod
    def is_startup(text):
        return any(key in text for key in VacancyFilter.STARTUP_KEYS)


class MessageParser:
    __CONTACT_PATTERNS = {
        'url': re.compile(r'([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])'),
        'email': re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+'),
        'username': re.compile(r'@\w+')
    }

    async def parse_message(self, message: Message, chat_username: str) -> Optional[VacancyData]:
        if not message.text and not message.caption:
            return None

        if MsgFilter().is_ads_and_img(message):
            return None

        # MAIN
        text = message.text
        text_low = text.lower()

        vacancy_filter = VacancyFilter()
        if not vacancy_filter.is_vacancy(text_low, chat_username):
            return None

        # bool
        level = False if vacancy_filter.is_senior_position(text_low) else True
        if PASS_SENIORS_TMP and level == False:
            return None
        remote = True if vacancy_filter.is_remote(text_low) else False
        startup = True if vacancy_filter.is_startup(text_low) else False

        is_bigtech = vacancy_filter.is_bigtech(text_low)

        contacts = self.extract_contacts(text_low)
        username = (
            message.sender_chat.username
            if message.sender_chat
            else (message.from_user.username if message.from_user else None)
        )
        user_tg_id = message.from_user.id if message.from_user else None
        user_image_id = message.from_user.photo.small_file_id if (
            message.from_user and message.from_user.photo) else None

        button_url = self.extract_button_url(message)
        chat_id = message.chat.id

        # tags = self.extract_tags(text_low)
        # print(tags)

        text_cleaned = re.sub(
            pattern=r'#[\wа-яА-ЯёЁ+]+', repl='', string=text)  # #\w+
        text_cleaned = text_cleaned.lstrip()

        try:
            v_data = VacancyData(
                level=level,
                remote=remote,
                startup=startup,
                is_bigtech=is_bigtech,
                text_=text_cleaned,
                contacts=contacts,
                user_username=username,
                user_tg_id=user_tg_id,
                user_image_id=user_image_id,
                posted_at=message.date,
                msg_url=message.link,
                chat_username=chat_username,
                chat_id=chat_id,
                views=message.views,
                button_url=button_url,
            )
        except ValidationError as e:
            logging.error(e)
            return None

        return v_data

    @staticmethod
    def extract_contacts(text: str) -> str:
        contacts = []
        for pattern_name, pattern in MessageParser.__CONTACT_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                if pattern_name == "url":
                    contacts.extend(["".join(match) for match in matches])
                else:
                    contacts.extend(matches)
        return "; ".join(contacts)

    @staticmethod
    def extract_button_url(message: Message) -> Optional[str]:
        if message.reply_markup and message.reply_markup.inline_keyboard:
            return message.reply_markup.inline_keyboard[0][0].url
        return None

    @staticmethod
    def extract_tags(text: str) -> List[str]:
        pattern = r"#[\wа-яА-ЯёЁ]+"
        return [tag.strip() for tag in re.findall(pattern, text)]


class DataSaver:
    @staticmethod
    async def save_to_csv(data: List[VacancyData]):
        if len(data) == 0:
            logging.error("Nothing to save")
            return None

        filename = f"""data1_jobs_{
            datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}_NEW.csv"""
        header = VacancyData.model_fields.keys()

        with open(filename, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=header, quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for row in data:
                writer.writerow(row.model_dump())

        logger.info(f"Done, CSV saved {len(data)} rows. File: {filename}")


class TelegramClient:
    def __init__(self, session_name: str = None, api_id: int = None, api_hash: str = None, phone_number: str = None,
                 password: str = None, session_string: str = None):
        if not session_name:
            logger.info("Starting in memory session client")
            self.client = Client(":memory:", session_string=session_string)

        else:
            self.client = Client(session_name, api_id, api_hash,
                                 phone_number=phone_number, password=password)

    async def __aenter__(self):
        await self.client.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.stop()

    @staticmethod
    async def progress(current, total):
        print(f"{current * 100 / total:.1f}%")

    async def file_id_to_bytes(self, file_id):
        # progress=self.progress
        file = await self.client.download_media(file_id, in_memory=True, block=True)
        file_bytes = bytes(file.getbuffer())
        file_name = file.name
        return file_bytes

    # parsed
    async def get_chat_data(self, chat_id: int, msg_limit: int) -> List[VacancyData]:
        chat_data = await self.client.get_chat(chat_id)
        logger.info(f"""Processing chat: {chat_data.title} - @{chat_data.username}""")

        messages: List[VacancyData] = []
        messages_set_text_255 = [] # for check unique
        
        async for message in self.client.get_chat_history(chat_id, limit=msg_limit):
            # pre filter + unique
            if message.date < MSG_MIN_DATE:
                continue

            parsed_message = await MessageParser().parse_message(
                message, chat_data.username
            )
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
            target_chats = [
                -1001328702818,
                -1001049086457,
                -1001154585596,
                -1001292405242,
                -1001650380394,
                -1001850397538,
                -1001164103043,  # new
            ]

        elif test_mode:
            target_chats = [-1001328702818,
                            -1001049086457,]
        self.target_chats = target_chats

    # @classmethod
    async def run(self) -> dict:
        """to get ids use forward to bot https://t.me/ShowJsonBot"""

        logger.warning(
            f"""Starting job search.
            Session name: {SESSION_NAME}; 
            TASK_EXECUTION_TIME_LIMIT: {TASK_EXECUTION_TIME_LIMIT}s;
            {MSG_LIMIT=}; 
            MSG MIN DATE: {MSG_MIN_DATE.strftime('%Y-%m-%d')}
            {UNIQUE_FILTER=}
            ======================================
            Pass seniors (temporary): {PASS_SENIORS_TMP}
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
            # upd: separate load user photos

            images_ids = set(
                [message.user_image_id for message in chat_results_flat])
            photos_ = await ImageUploader().upload(images_ids, client)

        # not separated by chats
        all_messages_new: List[VacancyData] = []
        hrs = {}
        # hrs_cnt = []
        errors = []

        for idx, result in enumerate(chat_results):
            logger.info(f"Chat {self.target_chats[idx]}: {len(result)}")
            if isinstance(result, Exception):
                if isinstance(result, asyncio.CancelledError):
                    logger.error(
                        f"asyncio.CancelledError in TASK get_chat_data", exc_info=result)
                elif isinstance(result, asyncio.TimeoutError):
                    logger.error(
                        f"asyncio.TimeoutError in TASK get_chat_data", exc_info=result)
                else:
                    logger.error(f"Error in get_chat_data", exc_info=result)
                errors.append(result)
            else:
                for message in result:
                    # check if channel
                    user_tg_id = message.user_tg_id
                    if not user_tg_id:
                        user_tg_id = message.chat_id

                    hrs.update({user_tg_id: message.user_username})

                    message.user_image_url = photos_.get(message.user_image_id)
                    all_messages_new.append(message)  # message.model_dump()

        unique_count = len(set([m.msg_url for m in all_messages_new]))
        logger.warning(f'Found {len(all_messages_new)}, unique msgs: {unique_count};\n'
                       f'Unique HRs {len(hrs)}. Errors: {len(errors)}')
        # post proc
        all_messages_new.sort(key=lambda x: x.posted_at, reverse=True)
        hr_data = tuple(hrs.items())

        return dict(all_messages=all_messages_new, hr_data=hr_data)


class ImageUploader:

    async def _upload_to_tgraph(self, f_bytes):
        async with ClientSession() as session:
            url = 'https://telegra.ph/upload'

            resp = await session.post(url, data={'file': f_bytes})
            response = await resp.json()

            if str(response) == 'Unknown error':
                logger.error('tg error: ' + response)
            pprint(response)
            return 'https://telegra.ph' + response[0]['src']

    async def _upload_to_catbox(self, f_bytes):
        url = 'https://catbox.moe/user/api.php'
        async with httpx.AsyncClient() as client:
            files = {
                'fileToUpload': ('img.jpg', f_bytes, 'image/jpeg')
            }

            data = {
                'reqtype': 'fileupload',
                'userhash': ''
            }

            resp = await client.post(url, files=files, data=data, timeout=10)
            response = resp.text
            return response

    async def uploader(self, f_bytes):
        if not f_bytes:
            raise ValueError("File is empty")

        try:
            # return await self._upload_to_tgraph(f_bytes)
            return await self._upload_to_catbox(f_bytes)
        except Exception as e:
            logging.error(msg=f'Error in upload img: {e}', exc_info=True)
            return 'err_upl'

    @classmethod
    async def download(cls, file_ids: list):
        pass

    # @classmethod
    async def upload(self, file_ids: list, client: TelegramClient) -> dict:
        files_dict = {}
        # for file_id in file_ids:
        while file_ids:
            file_id = file_ids.pop()
            if file_id is None:
                continue

            try:
                # block=False breaks program
                file = await client.client.download_media(file_id, in_memory=True)
                file_bytes = bytes(file.getbuffer())
                img_url = await self.uploader(file_bytes)
                files_dict.update({file_id: img_url})

            except ValueError:
                logging.error(f"File not found (None): {file_id}")
                continue

        return files_dict


if __name__ == "__main__":
    # start_time = asyncio.get_event_loop().time()
    # end_time = asyncio.get_event_loop().time()
    # logger.info(f"Total execution time: {end_time - start_time:.2f} seconds")

    # rich
    # from rich.traceback import install
    # install(show_locals=True)

    asyncio.run(ScrapeVacancies().run())
