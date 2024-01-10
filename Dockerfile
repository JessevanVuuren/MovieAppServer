FROM python:3.10.11 AS base

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

FROM base AS dev

CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9876", "--reload"]

FROM base AS pro

RUN chmod +x /app/env.sh


CMD ./env.sh && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
