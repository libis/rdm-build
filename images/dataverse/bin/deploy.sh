#!/usr/bin/env bash
################################################################################
# This script is to be used after Dataverse is (re)deployed
#
# It performs the changes that have to be made to the domain files
################################################################################

# Fail on any error
set -euo pipefail

# Load configuration
. "${SCRIPT_DIR}/config"

# Copy and fix jHove configuration files
cp "${DVINSTALL_DIR}/jhove"* "${DOMAIN_DIR}/config/"
sed -i "${DOMAIN_DIR}/config/jhove.conf" -e "s#file://.*/jhoveConfig\.xsd#file://${DOMAIN_DIR}/config/jhoveConfig.xsd#g"

