import logging
from datetime import datetime
from typing import Optional, Any, Literal, Callable, Annotated

from pydantic import BaseModel, Field, computed_field, field_serializer, field_validator, model_validator, \
    model_serializer, ConfigDict
import logging as log


class VacancyData(BaseModel):
    """v1909"""
    model_config = ConfigDict(
        extra="ignore",
        frozen=True,
    )

    level: bool # Literal["junior", "middle", "senior", "lead"]
    remote: bool
    startup: bool
    is_bigtech: Optional[bool] = Field(default=None)
    text_: Annotated[str, Field(max_length=4096)]
    contacts: Annotated[str, Field(max_length=4096)]
    user_username: Optional[str] = Field(default=None)
    posted_at: datetime
    msg_url: str
    chat_username: str
    chat_id: int = Field(gt=0)
    views: Optional[int]
    button_url: Optional[str] = Field(default=None) # exclude=True
    user_tg_id: Optional[int] = Field(default=None)
    user_image_id: Optional[str] = Field(default=None)
    user_image_url: Optional[str] = Field(default=None)

    @computed_field
    @property
    def posted_at_ts(self) -> int:
        return int(self.posted_at.timestamp())

    @field_serializer('posted_at', when_used='json')
    def serialize_date_ru(self, posted_at) -> str:
        return posted_at.strftime("%d/%m/%Y %H:%M")

    @field_serializer('user_image_url', when_used='json')
    def user_image_url_fmt(self, user_image_url) -> str:
        if user_image_url:
            return f'=image("{user_image_url}")'

    # @field_validator("chat_id")
    # @classmethod
    # def val_chat_id(cls, value):
    #     if value == 0:
    #         raise ValueError("chat_id = 0")
    #     return value

    @property
    def chat_username_PROP(self) -> str:
        if self.msg_url:
            return self.msg_url.split("/")[3]

    def model_dump_to_sheet_dict(self, **kwargs) -> dict[str, str | int]:
        _INCLUDE_VALUES_SET = {'level', 'remote', 'text_', 'msg_url', 'contacts', 'user_username', 'posted_at', 'posted_at_ts'}

        # log.warning(f'{_INCLUDE_VALUES_SET=}\n'
        # f'Размерность include (len {len(_INCLUDE_VALUES_SET)}): A:{chr(len(_INCLUDE_VALUES_SET) + 96)}')

        return super().model_dump(**kwargs, mode='json', include=_INCLUDE_VALUES_SET)

    # @computed_field
    # @cached_property
    # def deeplink_PROP(self) -> str:
    #     """docs: https://core.telegram.org/api/links#message-links"""
    #     if self.msg_url:
    #         chat = self.msg_url.split("/")[3]
    #         msg_id = self.msg_url.split("/")[4]
    #         return f"tg://resolve?domain={chat}&post={msg_id}"

    def as_dict(self) -> dict[str, str | int]:  # or .model_dump()
        return self.__dict__

class VacancySheetRow(VacancyData):
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
