FROM python:3.11-slim

WORKDIR /app

ENV POETRY_VERSION=1.4.2

RUN pip install poetry==$POETRY_VERSION

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry export --format=requirements.txt > requirements.txt

RUN pip install -r requirements.txt

COPY app .

RUN python manage.py collectstatic

FROM nginx:1.19.2-alpine
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/conf.d
COPY --from=0 app/static /app/static