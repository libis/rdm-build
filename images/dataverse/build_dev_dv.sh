#!/bin/bash

mkdir temp
cd temp
wget https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz
wget https://dlcdn.apache.org/maven/maven-3/3.9.5/binaries/apache-maven-3.9.5-bin.zip
tar -xzf openjdk-17.0.2_linux-x64_bin.tar.gz
unzip apache-maven-3.9.5-bin.zip
export JAVA_HOME=$PWD/jdk-17.0.2
export M2_HOME=$PWD/apache-maven-3.9.5
export PATH="$JAVA_HOME/bin:$M2_HOME/bin:$PATH"

cd ../../dataverse/modules/container-base
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}
cd ../../../dataverse
mvn -Pct clean package -Dbase.image=${DATAVERSE_BASE_IMAGE_TAG} -Dapp.image=${DATAVERSE_STOCK_IMAGE_TAG} -Dconf.image=${DATAVERSE_CONFIG_IMAGE_TAG} -Dbase.image.uid=${USER_ID} -Dbase.image.gid=${GROUP_ID}

cd ../rdm-build

mvn -version
rm -rf temp
