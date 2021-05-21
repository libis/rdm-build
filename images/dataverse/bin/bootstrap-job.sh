#!/usr/bin/env bash
################################################################################
# This script is used to bootstrap a Dataverse installation.
#
# It runs all necessary database foo that cannot be done from EclipseLink.
# It initializes the most basic settings and
# creates root dataverse and admin account.
################################################################################

# Load configuration
. "${SCRIPT_DIR}/config"

# Set BuiltinUsers Key
"${SCRIPT_DIR}/builtin-users-key.sh"
"${SCRIPT_DIR}/security-local.sh"

# Initialize common data structures to make Dataverse usable
"${DVINSTALL_DIR}/setup-all.sh"

# Initial configuration of Dataverse
"${SCRIPT_DIR}/config-job.sh"

# Configure Solr location
api PUT 'admin/settings/:SolrHostColonPort' -d "${SOLR_SERVICE_HOST}:${SOLR_SERVICE_PORT_HTTP}"

# Copy and fix jHove configuration files
cp "${DVINSTALL_DIR}/jhove"* "${DOMAIN_DIR}/config/"
sed -i "${DOMAIN_DIR}/config/jhove.conf" -e "s#file://.*/jhoveConfig\.xsd#file://${DOMAIN_DIR}/config/jhoveConfig.xsd#g"

# Configure security settings
"${SCRIPT_DIR}/security-token.sh"
"${SCRIPT_DIR}/builtin-users-disable.sh"
