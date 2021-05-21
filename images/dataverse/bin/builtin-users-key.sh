#!/usr/bin/env bash

. "${SCRIPT_DIR}/config"

echo "Setting Builtin Users Key"
api PUT 'admin/settings/BuiltinUsers.KEY' -d "${API_USERSKEY}" 
echo