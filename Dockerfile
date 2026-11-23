FROM python:3.11.15-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /skeleton
COPY . .

CMD ["sh", "-c", "python3 -B checks/run_all.py && python3 -B -m unittest discover -s tests"]
