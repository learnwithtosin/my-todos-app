FROM python:3.11.13-slim

WORKDIR /app

RUN pip install "fastapi[standard]"

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]