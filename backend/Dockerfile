FROM python:3.13.5-alpine3.21

ENV TZ=America/Bogota

RUN apk update && \
    apk add --no-cache \
        build-base \
        linux-headers \
        libffi-dev \
        musl-dev \
        postgresql-dev \
        python3-dev \
        py3-pip \
        tzdata

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app
RUN rm -f /app/.env
WORKDIR /app
EXPOSE 8000

CMD ["python3", "/app/main.py"]