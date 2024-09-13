ARG NODE_VERSION=18-alpine
ARG NGINX_VERSION=1.26.0-alpine

FROM node:${NODE_VERSION} AS builder

WORKDIR /app
ADD ./git /app/
ARG STAGE=dev
COPY ./config/${STAGE}/config.json /app/src/assets/config.json

RUN --mount=type=cache,target=/app/node_modules yarn install --network-timeout 300000

ARG NODE_ENV=production
ARG DATAVERSE_GLOBUS_UI_NAMESPACE=/globus
RUN --mount=type=cache,target=/app/node_modules\
  yarn ng build --configuration=${NODE_ENV} --base-href=DATAVERSE_GLOBUS_UI_NAMESPACE && \
  yarn ng run globus:build:${NODE_ENV}

FROM nginx:${NGINX_VERSION}

COPY --from=builder /app/dist/globus /usr/share/nginx/html
COPY ./config/nginx.conf /etc/nginx/conf.d/default.conf
