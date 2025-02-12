import csv
import logging
from datetime import datetime
from pprint import pprint
from typing import List

import aiohttp
import httpx

from src.PROJ.api.schemas_jobs import VacancyData

logger = logging.getLogger("rich")


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


class ImageUploader:
    async def _upload_to_tgraph(self, f_bytes):
        async with aiohttp.ClientSession() as session:
            url = 'https://telegra.ph/upload'

            resp = await session.post(url, data={'file': f_bytes}, timeout=10)
            response = await resp.json()

            logger.warning(f"upload img status: {response.status_code}, response: {response}")

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

            try:
                response = await client.post(url, files=files, data=data, timeout=10)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logger.error(f"upload img status: {e.response.status_code}, response: {e.response.text}")
                raise
            except httpx.TimeoutException as e:
                logger.error(f"upload img timeout: {e}")
                raise
            except Exception as e:
                logger.error(f"upload img error: {e}")
                raise

            logger.warning(f"upload img status: {response.status_code}, response: {response}")
            response = response.text
            return response

    async def uploader(self, f_bytes):
        if not f_bytes:
            raise ValueError("File is empty")

        try:
            return await self._upload_to_tgraph(f_bytes)
            # return await self._upload_to_catbox(f_bytes)
        except Exception as e:
            logging.error(msg=f'Error in upload img: {e}', exc_info=True)
            return 'err_upl'

    @classmethod
    async def download(cls, file_ids: list):
        pass

    # @classmethod
    async def upload(self, file_ids: list | set, client) -> dict:
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
