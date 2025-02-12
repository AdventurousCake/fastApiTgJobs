import logging
from datetime import datetime
from functools import cached_property
from typing import Optional, Any

from pydantic import BaseModel, Field, computed_field, field_serializer, model_validator, model_serializer

class VacancyData(BaseModel):
    """v0302"""

    level: bool
    remote: bool
    startup: bool
    is_bigtech: Optional[bool] = Field(default=None)

    text_: str
    contacts: str
    user_username: Optional[str] = Field(default=None)
    posted_at: datetime
    msg_url: str
    chat_username: str
    chat_id: int
    views: Optional[int]
    button_url: Optional[str] = Field(default=None) # exclude=True
    user_tg_id: Optional[int]
    user_image_id: Optional[str] = Field(default=None)
    user_image_url: Optional[str] = Field(default=None)

    @field_serializer('posted_at', when_used='json')
    def serialize_date_ru(self, posted_at) -> str:
        return posted_at.strftime("%d/%m/%Y %H:%M")

    @field_serializer('msg_url', when_used='json')
    def msg_url_fmt(self, msg_url) -> str:
        return f'=HYPERLINK("{msg_url}", "LINK")'
    
    @field_serializer('user_image_url', when_used='json')
    def user_image_url_fmt(self, user_image_url) -> str:
        if user_image_url:
            return f'=image("{user_image_url}")'

    @property
    def chat_username_PROP(self) -> str:
        if self.msg_url:
            return self.msg_url.split("/")[3]

    def as_dict(self) -> dict[str, str | int]:  # or .model_dump()
        return self.__dict__

    @model_validator(mode='before')
    @classmethod
    def check_str_limits(cls, data: Any) -> Any:
        """Filter ads; +db limits"""
        if isinstance(data, dict):
            for k, v in data.items():
                if k != 'text_' and isinstance(v, str):
                    try:
                        assert len(v) <= 256, f'{k} is too long. len: {len(v)}. Text: {v[:25]}'
                    except AssertionError:
                        logging.warning(f'Skip msg (ad)')

        return data

class VacancyDataGTableExport(VacancyData):
    # @computed_field
    # @cached_property #@property
    # def posted_at_date_ru(self) -> str:
    #     """for excel"""
    #     return self.posted_at.strftime("%d/%m/%Y %H:%M")

    def as_dict(self, exclude=None) -> dict[str, str | int]:
        d = self.__dict__
        return {k: v for k, v in d.items() if k not in exclude}
    
class VacancyDataDB(VacancyData):
    pass


class SHr(BaseModel):
    id: int
    username: str
    jobs: list[VacancyData]

    def as_dict(self) -> dict[str, str | int]:
        return self.__dict__
    

class Search(BaseModel):
    id: int
    date: datetime
    new_vacancies_count: int
    vacancies: list[VacancyData]
    
    def new_vacancies_count(self) -> int: ...
