import asyncio
import logging
import random

from faker import Faker
from sqlalchemy.dialects.postgresql import insert

from src.PROJ.api.schemas_jobs import VacancyData
from src.PROJ.core.db import async_session_factory, init_models
from src.PROJ.db.jobs_model import HR, Jobs

fake = Faker(locale="ru_RU")


# def generate_model_hr_pkdepends(dump=False) -> HR | dict:
#     username = fake.user_name()
#     hr = HR(username=username)
#     if dump:
#         return hr.model_dump()
#     return hr

def generate_model_vd(dump=False) -> VacancyData | dict:
    tg_url_schema = 'https://t.me/python_scripts_hr/' + str(random.randint(1000, 9999))
    tags_text = ['#vacancy', '#bigtech', '#remote', ' ']
    tags_text_str = ' '.join(tags_text)

    vd = VacancyData(
        level=fake.random_int(min=0, max=1),
        remote=fake.random_int(min=0, max=1),
        startup=fake.random_int(min=0, max=1),
        is_bigtech=fake.random_int(min=0, max=1),

        text_=tags_text_str + fake.text(max_nb_chars=50),
        contacts=fake.user_name(),
        user_username=fake.user_name(),
        user_tg_id=fake.random_int(min=100000, max=999999),
        user_image_id=str(fake.random_int(min=100000, max=999999)),
        user_image_url=fake.image_url(),

        posted_at=fake.date_time_this_month(),
        msg_url=tg_url_schema,
        # msg_url=fake.url(schemes=tg_url_schemas),
        chat_username=fake.user_name(),
        chat_id=fake.random_int(min=100000, max=999999),
        views=fake.random_int(min=0, max=1000),
    )
    if dump:
        return vd.model_dump()
    return vd


def generate_data(limit) -> tuple:
    vacancy_data = [generate_model_vd().as_dict() for _ in range(limit)]
    # vacancy_data = [generate_model(dump=True) for _ in range(10)]
    hr_data = [(vacancy.get("user_tg_id"), vacancy.get("user_username")) for vacancy in vacancy_data]
    return vacancy_data, hr_data


async def init_fake_data(limit=5):
    vacancy_data, hr_data = generate_data(limit)

    async with async_session_factory() as session:
        # hr first
        q1 = await session.scalars(insert(HR).values(hr_data).returning(HR.id))
        q2 = await session.scalars(insert(Jobs).values(vacancy_data).returning(Jobs.id))

        await session.commit()
        logging.info(f"inserted fake data {str(q1.all())};\n {str(q2.all())}")


async def main_test():
    await init_models()
    await init_fake_data()


if __name__ == '__main__':
    # pprint(generate_model().as_dict())
    asyncio.run(main_test())
