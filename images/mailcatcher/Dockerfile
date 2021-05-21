FROM ruby:2-alpine

ARG HTTP_PORT="1080"
ARG SMTP_PORT="1025"

ENV HTTP_PORT="S{HTTP_PORT}"
ENV SMTP_PORT="${SMTP_PORT}"

RUN set -e \
 && echo "Installing packages ..." \
 && apk add -q --no-cache --no-progress libstdc++ sqlite-libs build-base sqlite-dev \
 && echo "Installing gems ..." \
 && gem install --silent --no-document json mailcatcher \
 && echo "Cleaning up ..." \
 && apk del -q --purge build-base \
 && rm -rf /var/cache/apk/*

CMD mailcatcher --no-quit --foreground --ip=0.0.0.0 --smtp-port ${SMTP_PORT} --http-port ${HTTP_PORT}
