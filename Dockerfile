# create the app user
#RUN addgroup -S app_user && adduser -S app_user -G app_user


#FROM python:3.11-alpine; для alpine иногда нужна установка доп пакетов; slim-bullseye = debian
# Separate "build" image
FROM python:3.11-slim AS compile-image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefer-binary  -r requirements.txt

FROM python:3.11-slim
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY . /app

# "Run" image
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD ["uvicorn", "src.PROJ.api.app:app", "--host", "0.0.0.0", "--port", "8000"]

#export PYTHONPATH=$PYTHONPATH:/path/
#CMD ["python", "src/PROJ/api/app.py"]
