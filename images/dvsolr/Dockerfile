ARG SOLR_VERSION="9.3.0"
FROM solr:${SOLR_VERSION}

ARG SOLR_VERSION

USER root

ENV SOLR_OPTS="-Dsolr.jetty.request.header.size=102400"

# Run as solr user
USER ${SOLR_USER}
