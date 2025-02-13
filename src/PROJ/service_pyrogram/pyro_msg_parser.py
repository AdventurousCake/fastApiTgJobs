import logging
import re
from typing import Optional, List

from pydantic import ValidationError
from pyrogram.types import Message

from src.PROJ.api.schemas_jobs import VacancyData
from src.PROJ.core.config import PASS_SENIORS_TMP
from src.PROJ.service_pyrogram.pyro_msg_filters import MsgFilter, VacancyFilter


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
        user_username = (
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

        # clean #tags
        text_cleaned = re.sub(pattern=r'#[\wа-яА-ЯёЁ+]+', repl='', string=text)  # #\w+
        text_cleaned = text_cleaned.lstrip()

        try:
            v_data = VacancyData(
                level=level,
                remote=remote,
                startup=startup,
                is_bigtech=is_bigtech,
                text_=text_cleaned,
                contacts=contacts,
                user_username=user_username,
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
        return "\n".join(contacts)

    @staticmethod
    def extract_button_url(message: Message) -> Optional[str]:
        """tg button under msg"""
        if message.reply_markup and message.reply_markup.inline_keyboard:
            return message.reply_markup.inline_keyboard[0][0].url
        return None

    @staticmethod
    def extract_tags(text: str) -> List[str]:
        pattern = r"#[\wа-яА-ЯёЁ]+"
        return [tag.strip() for tag in re.findall(pattern, text)]
