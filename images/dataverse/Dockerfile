ARG PAYARA_VERSION=5.2021.3
FROM payara/server-full:${PAYARA_VERSION}-jdk11

# The first section requires root privileges
USER root

# Install software
RUN apt-get update -qqy; \
    echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections; \
    DEBIAN_FRONTEND=noninteractive apt-get -qq --no-install-recommends install -qqy \
    jq imagemagick wget curl less unzip postgresql-client ttf-mscorefonts-installer fontconfig; \
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
    DVINSTALL_DIR=${HOME_DIR}/dvinstall\
    JVM_ARGS="-XX:+HeapDumpOnOutOfMemoryError -XX:HeapDumpPath=\${ENV=DUMPS_DIR} -XX:MaxMetaspaceSize=512m -XX:MetaspaceSize=256m -Dfish.payara.classloading.delegate=false -XX:+UseG1GC -XX:+UseStringDeduplication -XX:+UseStringDeduplication -XX:+DisableExplicitGC"

# Create basic paths
RUN mkdir -p               ${DATA_DIR} ${DUMPS_DIR} ${UPLOAD_DIR} ${DVINSTALL_DIR} ${SCRIPT_DIR}/init.d \
 && chown -R payara:payara ${DATA_DIR} ${DUMPS_DIR} ${UPLOAD_DIR} ${DVINSTALL_DIR} ${SCRIPT_DIR}/init.d

# # Remove phonehome-bootstrap.jar from modules
# RUN rm ${PAYARA_DIR}/glassfish/modules/phonehome-bootstrap.jar

# NOTE: required? Why?
# Install esh template engine from Github
# RUN wget --quiet --no-verbose -O esh https://raw.githubusercontent.com/jirutka/esh/v0.3.0/esh \
#  && echo 'fe030e23fc1383780d08128eecf322257cec743b esh' | sha1sum -c - \
#  && chmod +x esh && mv esh /usr/local/bin/

# The rest needs to run as application user
USER payara

# Copy the dvinstall folder
COPY --chown=payara:payara dvinstall ${DVINSTALL_DIR}

# # Make docroot of Payara reside in higher level directory for easier targeting
# # Due to IQSS/dataverse-kubernetes#177: create the generated pathes so they are
# # writeable by us. TBR with #178.
# RUN mkdir -p ${DOMAIN_DIR}/generated/jsp/dataverse

# Symlink WAR file
# RUN ln -s ${DVINSTALL_DIR}/dataverse.war ${DEPLOY_DIR}/dataverse.war

# Copy across startup scripts
COPY --chown=payara:payara bin ${SCRIPT_DIR}
RUN chmod -R +x ${SCRIPT_DIR}
ENV PATH=${SCRIPT_DIR}:${PATH}

VOLUME ${DOMAIN_DIR}