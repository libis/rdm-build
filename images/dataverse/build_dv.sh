#!/bin/bash

mkdir temp
cd temp
#git clone --branch ${DATAVERSE_VERSION} --depth 1 https://github.com/IQSS/dataverse.git
# workaround -> patched
git clone --branch ${DATAVERSE_VERSION} https://github.com/IQSS/dataverse.git
cd dataverse
git cherry-pick 86ad64b33ac55972b9e1180b69b9629db21116bb 3a9568e5a458157dab514e0a42d71fac70aaea33 c93c8bd72d1f08699cab978b17d0f3c4b2ba8403 e67f53590f9bb8a59e2d1224000f58602fe97ab1 c2365416bbe73b23397c5221560e98432168ffdf 86f95719e53423dfc05b1b1442745d13b385cb08 192585e917f4d88b4ce1b531c4dc8af9e8d6e2a1 9464873b622c6dccea8f2f2f7451e3e682d7644c 3674a6f86c9df19ae0aac57ec4e3ebcee513fd01 b2b023a6c6c7a33214c80cd5cd3421c5735feb31 9f300752f3156d9c6c782dfcb514342dc4aafaeb aedc00ebca342df82611532b8cebb8da025740ac f3177bebb8eaf9f1dbcf49a3b0640baff5ed8ce9 bfcbb5dae9e8ebf64c2f9c7b2bb746aba3600646 f3c002586c57bf34ee5eb198677cdece33b989c2 ae733faa720dc9125cb5c0a1d438144b6438577a 55f43e0d30d7759cdcbd664f87b336f945be3566 19489b0246db6161a99fd0d9708a98f45993dfbe
cd ..
wget -O dataverse/modules/container-base/src/main/docker/Dockerfile https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/Dockerfile
wget -O dataverse/modules/container-base/src/main/docker/scripts/entrypoint.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/entrypoint.sh
cp ../images/dataverse/scripts/init_1_change_passwords.sh dataverse/modules/container-base/src/main/docker/scripts/init_1_change_passwords.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/init_1_generate_deploy_commands.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/init_1_generate_deploy_commands.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/init_1_generate_devmode_commands.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/init_1_generate_devmode_commands.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/removeExpiredCaCerts.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/removeExpiredCaCerts.sh
wget -O dataverse/modules/container-base/src/main/docker/scripts/startInForeground.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/modules/container-base/src/main/docker/scripts/startInForeground.sh
wget -O dataverse/src/main/docker/scripts/init_2_configure.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/src/main/docker/scripts/init_2_configure.sh
wget -O dataverse/src/main/docker/scripts/init_3_wait_dataverse_db_host.sh https://raw.githubusercontent.com/IQSS/dataverse/develop/src/main/docker/scripts/init_3_wait_dataverse_db_host.sh
# end workaround
cd dataverse/modules/container-base
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
cd ../../../dataverse
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dapp.image=${DATAVERSE_STOCK_IMAGE_TAG} -Dconf.image=${DATAVERSE_CONFIG_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
cd ../..
mvn -version
rm -rf temp
