# build
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade setuptools \
 && pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir --prefer-binary --user -r requirements.txt

# use build
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

CMD ["uvicorn", "src.PROJ.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
