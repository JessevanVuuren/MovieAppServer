FROM python:3.10.11 AS base

WORKDIR /app

COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS dev

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9876", "--reload"]

FROM base AS pro

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6789"]
