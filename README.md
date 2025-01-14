# Simple Fastapi telegram jobs parser

[//]: # (![Python]&#40;https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54&#41;)
[//]: # (![Python]&#40;https://github.com/AdventurousCake/PROJNAME/actions/workflows/tests.yml/badge.svg?branch=main&#41;)
![Static Badge](https://img.shields.io/badge/python-3.10+-black?logo=python&logoColor=edb641&labelColor=202235&color=edb641)
![Python](https://github.com/AdventurousCake/fastApiTgJobs/actions/workflows/python-app.yml/badge.svg?branch=master)

[//]: # (![Static Badge]&#40;https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-black?logo=python&logoColor=edb641&labelColor=202235&color=edb641&#41;)

Парсер вакансий телеграм-каналов

## Пример использования
1. Получить сессию pyrogram, сохранить в src/PROJ/service_pyrogram
2. Заполнить env файл
3. Запустить uvicorn src.PROJ.api.app:app --host 0.0.0.0 --port 9000
4. Открыть в браузере localost:9000
## URLs:

### /jobs/jobs_all
Возвращает список вакансий

### /jobs/hrs_all
Возвращает список HR

### /docs
Возвращает swagger документацию