FROM python:3.11

WORKDIR /app

ENV POETRY_VERSION=1.4.2

#RUN apt-get update наскольно необходима тут эта команда, изза нее все сильно дольше собиратеся, ниже думаю ее тоже не вариант ставить 

RUN pip install poetry==$POETRY_VERSION

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry export --format=requirements.txt > requirements.txt

RUN pip install -r requirements.txt

COPY app .