ARG SOLR_VERSION="8.8.2"
FROM solr:${SOLR_VERSION}-slim

ARG SOLR_VERSION

USER root

# Install Curl
RUN apt-get update -qqy; \
    DEBIAN_FRONTEND=noninteractive apt-get -qq --no-install-recommends install -qqy curl ed bc; \
    rm -rf /var/lib/apt/lists/*

# Change solr user and group id
ARG USER_ID="1000"
ARG GROUP_ID="1000"
RUN echo "Changing user and group id ..." \
 && usermod -u ${USER_ID} ${SOLR_USER} \
 && groupmod -g ${GROUP_ID} ${SOLR_GROUP} \
 && echo "Fixing file user ownership ..." \
 && find / -xdev -user ${SOLR_UID} -exec chown ${USER_ID} {} \; \
 && echo "Fixing file group ownership ..." \
 && find / -xdev -group ${SOLR_GID} -exec chgrp ${GROUP_ID} {} \;

ENV SOLR_OPTS="-Dsolr.jetty.request.header.size=102400"

# Run as solr user
USER ${SOLR_USER}
