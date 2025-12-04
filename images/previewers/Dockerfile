FROM nginx:latest

ENV VERSIONS="v1.5"

ENV NGINX_HTTP_PORT=80
ENV NGINX_HTTPS_PORT=443

RUN apt update && apt install wget

# Copy the template file to the container
COPY conf/nginx.conf.template /etc/nginx/templates/nginx.conf.template

COPY scripts/init.sh /docker-entrypoint.d

WORKDIR /app
COPY git /app
COPY dvwebloader /app/dvwebloader

RUN chmod +x /docker-entrypoint.d/init.sh \
        && chmod +x /app/localinstall.sh \
        && chmod +x /app/dvwebloader/localinstall.sh
