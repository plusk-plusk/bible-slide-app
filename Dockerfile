FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:10000", "app:app"]
