# build
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

# run image
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD ["uvicorn", "src.PROJ.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
