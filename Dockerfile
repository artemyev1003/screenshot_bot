FROM python:latest

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/

RUN python -m pytest tests/*

CMD ["python", "bot.py"]
