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

# Install configuration defaults
RUN cp -r /opt/solr/server/solr/configsets/_default /opt/solr/server/solr/configsets/dataverse \
 && rm /opt/solr/server/solr/configsets/dataverse/conf/managed-schema
COPY conf/* /opt/solr/server/solr/configsets/dataverse/conf/

# Install the update schema script
COPY scripts/* /opt/docker-solr/scripts/

# Patch the copied files
RUN sed -i -e "s#<luceneMatchVersion>[0-9.]*</luceneMatchVersion>#<luceneMatchVersion>${SOLR_VERSION}</luceneMatchVersion>#" \
        /opt/solr/server/solr/configsets/dataverse/conf/solrconfig.xml \
 && chmod 755 /opt/docker-solr/scripts/updateSchema.sh

# Run as solr user
USER ${SOLR_USER}
CMD ["solr-precreate", "collection1", "dataverse"]

## Prepare schema updater sidecar
#ARG WEBHOOK_VERSION=2.8.0
#RUN wget --no-verbose -O webhook.tar.gz https://github.com/adnanh/webhook/releases/download/${WEBHOOK_VERSION}/webhook-linux-amd64.tar.gz && \
#    tar -xzf webhook.tar.gz --strip-components=1 -C ${SCHEMA_SCRIPT_DIR} && \
#    rm webhook.tar.gz && \
#    chmod +x ${SCHEMA_SCRIPT_DIR}/*.sh
