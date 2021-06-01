FROM ruby:3-buster

ARG APP_PATH=/opt/app
ARG APP_USER=app
ARG APP_GROUP=app
ARG APP_USER_ID=1000
ARG APP_GROUP_ID=1000

COPY docker-entrypoint.sh /usr/bin

RUN chmod +x /usr/bin/docker-entrypoint.sh \
 && gem install bundler \
 && groupadd --gid ${APP_GROUP_ID} ${APP_GROUP} \
 && useradd --home-dir ${APP_PATH} --create-home --uid ${APP_USER_ID} --gid ${APP_GROUP} --no-user-group --shell /bin/bash ${APP_USER} \
 && echo ". ./setup.sh" >> ${APP_PATH}/.bashrc

WORKDIR ${APP_PATH}

COPY --chown=${APP_USER}:${APP_GROUP} Gemfile* *.rb *.sh ${APP_PATH}/

RUN bundle install && chmod +x *.rb *.sh

USER ${APP_USER}

ENTRYPOINT [ "docker-entrypoint.sh" ]

CMD ["irb"]
