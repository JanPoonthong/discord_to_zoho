FROM python:3.9

RUN mkdir -p /var/discord

WORKDIR /var/discord

COPY ./ /var/discord

COPY requirements.txt /var/discord
RUN pip install -r requirements.txt

ENTRYPOINT python /var/discord/main.py
