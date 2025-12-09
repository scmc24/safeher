FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    python3 gcc libc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installer pip et dépendances Python
RUN pip install --upgrade pip
COPY ./requirements.txt /requirements.txt
RUN pip install -r requirements.txt

# Créer le dossier app
RUN mkdir /app
WORKDIR /app
COPY ./bot /app


COPY ./bot/start.sh .
RUN sed -i 's/\r$//g' /app/start.sh
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]
