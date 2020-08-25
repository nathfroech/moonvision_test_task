FROM python:3.8

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./requirements/staging.txt requirements.txt

RUN pip install -U pip &&\
    pip install -r requirements.txt

COPY ./ .

RUN python helpers/generate_env_file.py &&\
    sed -i "s/PROJECT_ENVIRONMENT = debug/PROJECT_ENVIRONMENT = production/" .env
RUN python manage.py migrate
RUN python manage.py collectstatic

# Ideally there would be a separate script which would wait for db container start and then perform migrate
# and runserver.
# --insecure is to make Django handle static by itself, because we don't have nginx or something else for this
ENTRYPOINT python manage.py runserver 0.0.0.0:8000 --insecure
