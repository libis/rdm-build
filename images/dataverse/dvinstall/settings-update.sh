#!/usr/bin/env bash

. ${SCRIPT_DIR}/config
. ${DVINSTALL_DIR}/setup-tools

${SCRIPT_DIR}/config-job.sh

command -v jq &>/dev/null || { echo >&2 '`jq` ("sed for JSON") is required, but not installed. Aborting.'; exit 1; }

echo "Application settings update ..."
settings_loop 'admin/settings' settings
echo
