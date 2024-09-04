from datetime import datetime
from functools import cached_property
from typing import Optional

from pydantic import BaseModel, Field, computed_field, field_serializer


class VacancyData(BaseModel):
    """v04.09"""

    level: bool
    remote: bool
    startup: bool
    is_bigtech: Optional[bool] = Field(default=None)

    text_: str
    contacts: str
    user_username: Optional[str] = Field(default=None)
    user_tg_id: Optional[int]
    user_image_id: Optional[str] = Field(default=None)
    user_image_url: Optional[str] = Field(default=None)
    posted_at: datetime
    msg_url: str
    chat_username: str
    chat_id: int
    views: Optional[int]
    button_url: Optional[str] = Field(default=None)

    @field_serializer('posted_at', when_used='json')
    def serialize_date_ru(self, posted_at) -> str:
        return posted_at.strftime("%d/%m/%Y %H:%M")

    @property
    def chat_username_PROP(self) -> str:
        if self.msg_url:
            return self.msg_url.split("/")[3]

    # @computed_field
    # @cached_property
    # def posted_at_date_ru(self) -> str:
    #     """for excel"""
    #     return self.posted_at.strftime("%d/%m/%Y %H:%M")

    # or .model_dump()
    def as_dict(self) -> dict[str, str | int]:
        return self.__dict__


class SHr(BaseModel):
    id: int
    username: str
    jobs: list[VacancyData]

    def as_dict(self) -> dict[str, str | int]:
        return self.__dict__
