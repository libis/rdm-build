#!/usr/bin/env bash

# Load configuration
. "${SCRIPT_DIR}/config"
. ${DVINSTALL_DIR}/setup-tools

[[ -z "$1" ]] || adminKey="$1"

echo ">>> Custom setup <<<"
echo

${CUSTOM_INSTALL}/customize-properties.sh
