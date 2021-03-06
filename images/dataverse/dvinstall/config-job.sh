#!/usr/bin/env bash
################################################################################
# This script is used to configure a Dataverse installation from a ConfigMap.
# It is used solely for changing Database settings!
################################################################################

# Fail on any error
set -euo pipefail

. "${SCRIPT_DIR}/config"

echo -e "Running configuration job for Dataverse."

# Set Database options based on environment variables db_XXX from ConfigMap
echo "Setting Database options"
if `env | grep -Ee '^db_' &>/dev/null`; then
  env -0 | grep -z -Ee "^db_" | while IFS='=' read -r -d '' k v; do
      KEY=`echo "${k}" | sed -e 's/^db_/:/'`
      echo -e "  ... ${KEY}=${v}"
      if [[ -z "${v}" ]]; then
        # empty var => delete the setting
        api DELETE "admin/settings/${KEY}"
      else
        # set the setting
        api PUT "admin/settings/${KEY}" -d "${v}"
      fi
  done
else
  echo "  none found"
fi
echo

. ${DVINSTALL_DIR}/setup-tools

# Custom configuration
CUSTOMSCRIPT="${CUSTOM_INSTALL}/config-job.sh"
[[ -e "${CUSTOMSCRIPT}" ]] && "${CUSTOMSCRIPT}"
