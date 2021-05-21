#!/usr/bin/env bash

################################################################################
# Add Dataverse app to deploy dir when not yet deployed.
#
# It is necessary to do this before the init_1 script starts as it will perform
# the deployment for any app in the deploy dir.
################################################################################

# Add Dataverse app to deploy dir
if test -d "${DOMAIN_DIR}/applications/dataverse"
then
  echo "Dataverse already deployed"
else
  echo "Deploying Dataverse application"
  ln -s "${DVINSTALL_DIR}/dataverse.war" "${DEPLOY_DIR}/dataverse.war"
fi
