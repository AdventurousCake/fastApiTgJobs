from datetime import datetime
from enum import Enum, auto
from typing import Annotated, Optional
from sqlalchemy import String, DateTime, UniqueConstraint, ForeignKey, text, Index, BigInteger, Text, Computed, \
    Constraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.PROJ.core.db import Base, str_256


class Level(Enum):
    junior = auto()
    middle = auto()
    senior = auto()


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True)]
int64pk = Annotated[int, mapped_column(BigInteger, primary_key=True, autoincrement=False)]
int64pk_auto = Annotated[int, mapped_column(BigInteger, primary_key=True, autoincrement=True)]

big_int = Annotated[int, mapped_column(BigInteger)]

date_default_none = Annotated[DateTime, mapped_column(DateTime, default=None)]
date_default_now = Annotated[DateTime, mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"))]
updated_at = Annotated[DateTime, mapped_column(DateTime,
                                               server_default=text("TIMEZONE('utc', now())"),
                                               onupdate=datetime.utcnow())
    # DateTime, mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
]


class IntIdPkMixin:
    id: Mapped[intpk]


class DefaultBase(Base):
    __abstract__ = True
    id: Mapped[int64pk]
    created_at: Mapped[date_default_now]
    updated_at: Mapped[updated_at]


class HR(Base):
    __tablename__ = "hr"
    id: Mapped[int64pk]
    username: Mapped[str_256 | None]

    jobs = relationship("Jobs", back_populates="hr", lazy="joined")


class Jobs(Base):
    __tablename__ = "jobs"

    id: Mapped[intpk]
    level: Mapped[bool]
    startup: Mapped[bool]
    remote: Mapped[bool]
    is_bigtech: Mapped[Optional[bool]] = mapped_column(default=None)

    text_: Mapped[str] = mapped_column(Text, CheckConstraint('length(text_)<=4096'), nullable=False)
    md5_text: Mapped[str] = mapped_column(String(32), Computed("md5(text_)", persisted=True), nullable=False)

    contacts: Mapped[str] = mapped_column(String(4096), nullable=True)
    user_tg_id: Mapped[big_int]
    user_username: Mapped[str_256 | None]
    user_image_id: Mapped[str_256 | None]
    user_image_url: Mapped[str_256 | None]
    msg_url: Mapped[str_256 | None]
    chat_username: Mapped[str_256 | None]
    chat_id: Mapped[big_int | None]
    # chat_username: Mapped[str_256 | None] = mapped_column(Computed('msg_url'))
    views: Mapped[Optional[int]] = mapped_column(default=0)
    button_url: Mapped[str_256 | None]
    user_tg_id: Mapped[big_int | None] = mapped_column(ForeignKey("hr.id", ondelete="CASCADE"))
    hr = relationship("HR", back_populates="jobs", lazy="joined")  # cascade="all, delete") # use_list=True
    # hr: Mapped['HR'] = relationship(back_populates="jobs")
    is_new: Mapped[bool] = mapped_column(default=True)  # according .clean_isnew()
    posted_at: Mapped[date_default_none]
    parsed_at: Mapped[date_default_now]
    updated_at: Mapped[updated_at]

    @property
    def chat_username_PROP(self) -> str | None:
        if self.msg_url:
            return self.msg_url.split("/")[3]

    __table_args__ = (
        # UniqueConstraint("msg_url", "text_", name="idx_uniq_link_text"),
        UniqueConstraint("msg_url", "md5_text", name="idx_uniq_link_text"),
        Index("idx_msg_url", "msg_url"),
        Index("idx_user_tg_id", "user_tg_id"),  # fkey index
    )
