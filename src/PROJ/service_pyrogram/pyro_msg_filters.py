import re


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
    SENIOR_KEYS = ("#lead", "senior", "#teamlead ", "team lead", "#techlead")
    SENIOR_KEYS_EXCLUDE = ("middle", "junior")
    REMOTE_KEYS = ("#удаленка", "#remote", "#удаленно")
    STARTUP_KEYS = ("стартап", "startup")
    BIGTECH_RU_KEYS = ("yandex", "sber", 'яндекс', 'сбер', 'team.vk', 'kaspersky')

    ONLY_VACANCIES_CHANNELS = ("job_python", "python_djangojobs", "p_rabota")
    OFFICE_KEYS = ("#офис",)

    @staticmethod
    def simple_filter(text, keys) -> bool:
        return any(key in text for key in keys)

    @staticmethod
    def is_bigtech(text):
        return VacancyFilter.simple_filter(text, VacancyFilter.BIGTECH_RU_KEYS)

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
