# -> image: flask:dede-manu
FROM python:3.10-alpine3.20

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
  TZ="Europe/Paris" \
  SECRET_KEY="changeme"

RUN  \
  apk update && \
  apk add ffmpeg tzdata && \
  rm -fR /var/cache/apk/* && \
  \
  adduser -D flask -u 55555 && \
  chown -R flask.flask /app

# le moteur flask
# requirements.txt doit être mis à jour via setup.make-requirements.sh
COPY --chown=flask:flask README.md setup.py requirements.txt /app/
RUN \
  pip install --upgrade pip && \
  pip install . && \
  pip install yt-dlp && \
  python3 -m pip install -U https://github.com/coletdjnz/yt-dlp-youtube-oauth2/archive/refs/heads/master.zip

EXPOSE ${port}
CMD flask run -h 0.0.0.0 -p $PORT

# le code source
COPY --chown=flask:flask . /app/

# ADD https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp /usr/local/bin/yt-dlp
# RUN chmod a+rx /usr/local/bin/yt-dlp

USER flask
RUN mkdir instance
