# -> image: flask:dede-manu
FROM python:3.8.12-alpine3.14

WORKDIR /app

ARG port=5000

# Si la variable d'environnement REDIS est positionné avec comme valeur ADDRESS:PORT, 
# alors ce serveur est utilsé pour les sessions
# Rappel: le port clasique de Redis est: 6379

# si la variable d'environnement TZ="Europe/Paris", tzdata règle le fuseau horaire

ENV \
  FLASK_APP=manu_dede \
  PORT=${port} \
  PATH=/home/flask/.local/bin:$PATH \
  PYTHONUNBUFFERED=1 \
  TZ="Europe/Paris"

RUN  \
  apk update && \
  apk add ffmpeg tzdata sqlite && \
  rm -fR /var/cache/apk/* && \
  \
  adduser -D flask -u 55555 && \
  chown -R flask.flask /app

# le moteur flask
COPY --chown=flask:flask README.md setup.py requirements.txt /app/
RUN pip install .

EXPOSE ${port}
CMD ["/app/run-init.sh"]

# le code source
COPY --chown=flask:flask . /app/

ADD https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp /usr/local/bin/yt-dlp
RUN chmod a+rx /usr/local/bin/yt-dlp

USER flask
