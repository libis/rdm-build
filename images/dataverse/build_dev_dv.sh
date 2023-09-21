#!/bin/bash

cd ../dataverse/modules/container-base
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
cd ../../../dataverse
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dapp.image=${DATAVERSE_STOCK_IMAGE_TAG} -Dconf.image=${DATAVERSE_CONFIG_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
