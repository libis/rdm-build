#!/bin/bash

mkdir temp
cd temp
git clone --branch ${DATAVERSE_VERSION} --depth 1 https://github.com/IQSS/dataverse.git
wget -O dataverse/modules/container-base/src/main/docker/Dockerfile https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/Dockerfile
wget -O dataverse/modules/container-base/src/main/docker/scripts/entrypoint.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/entrypoint.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/init_1_change_passwords.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/init_1_change_passwords.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/init_1_generate_deploy_commands.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/init_1_generate_deploy_commands.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/init_1_generate_devmode_commands.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/init_1_generate_devmode_commands.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/removeExpiredCaCerts.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/removeExpiredCaCerts.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/startInForeground.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/startInForeground.sh
wget -O dataverse/src/main/docker/scripts/init_2_configure.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/src/main/docker/scripts/init_2_configure.sh
wget -O dataverse/src/main/docker/scripts/init_3_wait_dataverse_db_host.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/src/main/docker/scripts/init_3_wait_dataverse_db_host.sh
cd dataverse/modules/container-base
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
cd ../../../dataverse
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dapp.image=${DATAVERSE_STOCK_IMAGE_TAG} -Dconf.image=${DATAVERSE_CONFIG_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
cd ../..
mvn -version
rm -rf temp
