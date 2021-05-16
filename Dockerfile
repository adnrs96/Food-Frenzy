FROM python:3.8-slim

RUN apt-get update
RUN apt-get install -y libpq-dev

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

EXPOSE 8000

COPY app_frenzy app_frenzy
COPY scripts scripts
COPY entrypoint.sh entrypoint.sh

ENV DEBUG False
ENV INIT_DB false

CMD ["bash", "entrypoint.sh"]