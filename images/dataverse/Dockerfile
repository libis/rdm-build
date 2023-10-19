ARG DATAVERSE_STOCK_IMAGE_TAG="rdm/dataverse-stock:1.5"
FROM "${DATAVERSE_STOCK_IMAGE_TAG}"

ARG DATAVERSE_STOCK_IMAGE_TAG

# The first section requires root privileges
USER root

# Install software
RUN apt-get install -qqy ruby
