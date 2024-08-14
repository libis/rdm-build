#!/bin/bash

mkdir temp
cd temp
git clone --branch ${DATAVERSE_VERSION} --depth 1 https://github.com/IQSS/dataverse.git
cd dataverse/modules/container-base
cd src/main/docker
wget -O Dockerfile https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/Dockerfile
cd ../../..
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
cd ../../../dataverse
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dapp.image=${DATAVERSE_STOCK_IMAGE_TAG} -Dconf.image=${DATAVERSE_CONFIG_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
cd ../..
mvn -version
rm -rf temp
