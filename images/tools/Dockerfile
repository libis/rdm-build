FROM ruby:3-buster

ARG APP_PATH=/opt/app
ARG APP_USER=app
ARG APP_GROUP=app
ARG APP_USER_ID=1000
ARG APP_GROUP_ID=1000

RUN apt-get update -qqy \
 && DEBIAN_FRONTEND=noninteractive apt-get -qq --no-install-recommends install -qqy python3-pip python3-venv \
 && rm -rf /var/lib/apt/lists/*

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

# Install Python virtual environment with required modules
RUN python3 -m venv venv \
 && . $HOME/venv/bin/activate \
 && pip install --upgrade pip \
 && pip install setuptools configparser numpy pandas pyDataverse pysftp requests \
 && echo ". ./venv/bin/activate" >> ${APP_PATH}/.bashrc

COPY rdmPyTools ${APP_PATH}/rdmPyTools

CMD ["irb"]
