ARG BASE_VERSION=unstable
FROM gdcc/base:${BASE_VERSION}

# The first section requires root privileges
USER root

# Install software
RUN apt-get update -qqy; \
    echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections; \
    DEBIAN_FRONTEND=noninteractive apt-get -qq --no-install-recommends install -qqy \
    jq imagemagick wget curl less unzip postgresql-client ttf-mscorefonts-installer fontconfig ruby ed bc sed gawk; \
    rm -rf /var/lib/apt/lists/*

# Change application user and group id
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN usermod -u ${USER_ID} payara \
 && groupmod -g ${GROUP_ID} payara
RUN chown -R -h payara:payara ${HOME_DIR} &>/dev/null || true

# paths
ENV DATA_DIR=/data\
    SECRETS_DIR=/run/secrets\
    DUMPS_DIR=/dumps\
    UPLOAD_DIR=/uploads\
    DOMAIN_DIR=${PAYARA_DIR}/glassfish/domains/${DOMAIN_NAME}\
    DVINSTALL_DIR=${HOME_DIR}/dvinstall

# Create basic paths
RUN mkdir -p               ${DATA_DIR} ${DUMPS_DIR} ${UPLOAD_DIR} ${DVINSTALL_DIR} ${SCRIPT_DIR}/init.d \
&& chown -R payara:payara ${DATA_DIR} ${DUMPS_DIR} ${UPLOAD_DIR} ${DVINSTALL_DIR} ${SCRIPT_DIR}/init.d

# The rest needs to run as application user
USER payara

# deploy WAR file
ARG DATAVERSE_WAR_URL=https://github.com/IQSS/dataverse/releases/download/v6.4/dataverse-6.4.war
ADD --chown=payara:payara ${DATAVERSE_WAR_URL} ${DEPLOY_DIR}

VOLUME ${DOMAIN_DIR}/docroot
WORKDIR ${DOMAIN_DIR}/docroot