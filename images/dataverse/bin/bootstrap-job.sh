#!/usr/bin/env bash
################################################################################
# This script is used to bootstrap a Dataverse installation.
#
# It runs all necessary database foo that cannot be done from EclipseLink.
# It initializes the most basic settings and
# creates root dataverse and admin account.
################################################################################

# Fail on any error
set -euo pipefail

# Load configuration
. "${SCRIPT_DIR}/config"

# Set API local only and BuiltinUsers Key
api_only_local
builtin_enable

# Initialize common data structures to make Dataverse usable
"${DVINSTALL_DIR}/setup-all.sh"

# Initial configuration of Dataverse
"${SCRIPT_DIR}/config-job.sh"

# Configure Solr location
api PUT 'admin/settings/:SolrHostColonPort' -d "${SOLR_SERVICE_HOST}:${SOLR_SERVICE_PORT_HTTP}"

# Copy and fix jHove configuration files
cp "${DVINSTALL_DIR}/jhove"* "${DOMAIN_DIR}/config/"
sed -i "${DOMAIN_DIR}/config/jhove.conf" -e "s#file://.*/jhoveConfig\.xsd#file://${DOMAIN_DIR}/config/jhoveConfig.xsd#g"

# Configure final security settings
api_by_token
builtin_disable
